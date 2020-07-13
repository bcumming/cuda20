#include <iostream>
#include <fstream>
#include <cstdio>
#include <cstdlib>
#include <ctime>

#include <cuda.h>

#include "util.hpp"
#include "cuda_stream.hpp"

// 2D diffusion example
// the grid has a fixed width of nx=128
// the use specifies the height, ny, as a power of two
// note that nx and ny have 2 added to them to account for halos

template <typename T>
void fill_gpu(T *v, T value, int n);

void write_to_file(int nx, int ny, double* data);

template <typename T>
void fill_random_ones(T* v, double probability, int n);

template <typename T>
void fill_hole(T* v, int n, int nx, int ny);

__global__
void reactiondiffusion_u(double *u0, double *u1, double *v0, int nx, int ny, double dt) {
    int i = threadIdx.x + blockDim.x*blockIdx.x + 1;
    int j = threadIdx.y + blockDim.y*blockIdx.y + 1;

    double d_u = 0.01;
    double f   = 0.035;

    if (i<nx-1 && j<ny-1) {
        int pos = nx*j + i;
        double v0_pos = v0[pos];
        double u0_pos = u0[pos];

        u1[pos] = u0_pos + dt * (d_u*(-4.*u0_pos
                     + u0[pos-1] + u0[pos+1]
                     + u0[pos-nx] + u0[pos+nx])
                     - u0_pos*v0_pos*v0_pos + f*(1 - u0_pos));

    }
}

__global__
void reactiondiffusion_v(double *v0, double *v1, double *u0, int nx, int ny, double dt) {
    int i = threadIdx.x + blockDim.x*blockIdx.x + 1;
    int j = threadIdx.y + blockDim.y*blockIdx.y + 1;

    double d_v = 0.005;
    double f   = 0.035;
    double k   = 0.065;

    if (i<nx-1 && j<ny-1) {
        int pos = nx*j + i;
        double v0_pos = v0[pos];
        double u0_pos = u0[pos];

        v1[pos] = v0_pos + dt * (d_v*(-4.*v0_pos
                        + v0[pos-1] + v0[pos+1]
                        + v0[pos-nx] + v0[pos+nx])
                        + u0_pos*v0_pos*v0_pos - v0_pos*(f + k));

    }
}
// TODO : implement stencil using 2d launch configuration
// NOTE : i-major ordering, i.e. x[i,j] is indexed at location [i+j*nx]
//  for(i=1; i<nx-1; ++i) {
//    for(j=1; j<ny-1; ++j) {
//        x1[i,j] = x0[i,j] + dt * (-4.*x0[i,j]
//                   + x0[i,j-1] + x0[i,j+1]
//                   + x0[i-1,j] + x0[i+1,j]);
//    }
//  }

int main(int argc, char** argv) {
    // set up parameters
    // first argument is the y dimension = 2^arg
    size_t pow    = read_arg(argc, argv, 1, 8);
    // second argument is the number of time steps
    size_t nsteps = read_arg(argc, argv, 2, 100);

    // set domain size
    size_t nx = (1 << pow)+2;
    size_t ny = (1 << pow)+2;
    double dt = 0.1;

    std::cout << "\n## " << nx << "x" << ny
              << " for " << nsteps << " time steps"
              << " (" << nx*ny << " grid points)"
              << std::endl;

    // allocate memory on device and host
    // note : allocate enough memory for the halo around the boundary
    auto buffer_size = nx*ny;
    double *u_host = malloc_host<double>(buffer_size);
    double *u0     = malloc_device<double>(buffer_size);
    double *u1     = malloc_device<double>(buffer_size);

    double *v_host = malloc_host<double>(buffer_size);
    double *v0     = malloc_device<double>(buffer_size);
    double *v1     = malloc_device<double>(buffer_size);

    // set random initial conditions of 0s and 1s everywhere
    fill_random_ones(u_host, 0.001, buffer_size);
    fill_hole(u_host, buffer_size, nx, ny);
    copy_to_device(u_host, u0, buffer_size);
    copy_to_device(u_host, u1, buffer_size);

    fill_random_ones(v_host, 0.01, buffer_size);
    copy_to_device(v_host, v0, buffer_size);
    copy_to_device(v_host, v1, buffer_size);

    // set boundary conditions of 1 on south border
    // fill_gpu(x0, 1., nx);
    // fill_gpu(x1, 1., nx);
    // fill_gpu(x0+nx*(ny-1), 1., nx);
    // fill_gpu(x1+nx*(ny-1), 1., nx);

    cuda_stream stream;
    cuda_stream copy_stream();
    auto start_event = stream.enqueue_event();

    // time stepping loop
    auto find_num_blocks = [](int x, int bdim) {return (x+bdim-1)/bdim;};
    dim3 block_dim(16, 16);
    int nbx = find_num_blocks(nx-2, block_dim.x);
    int nby = find_num_blocks(ny-2, block_dim.y);
    dim3 grid_dim(nbx, nby);
    
    for(auto step=0; step<nsteps; ++step) {
        // TODO: launch the diffusion kernel in 2D
        reactiondiffusion_u<<<grid_dim, block_dim>>>(u0, u1, v0, nx, ny, dt);

        reactiondiffusion_v<<<grid_dim, block_dim>>>(v0, v1, u0, nx, ny, dt);

        std::swap(u0, u1);
        std::swap(v0, v1);
    }
    auto stop_event = stream.enqueue_event();
    stop_event.wait();

    copy_to_host<double>(u0, u_host, buffer_size);
    copy_to_host<double>(v0, v_host, buffer_size);

    double time = stop_event.time_since(start_event);

    std::cout << "## " << time << "s, "
              << nsteps*(nx-2)*(ny-2) / time << " points/second"
              << std::endl << std::endl;

    std::cout << "writing to output.bin/bov" << std::endl;
    write_to_file(nx, ny, u_host);

    return 0;
}

template <typename T>
__global__
void fill(T *v, T value, int n) {
    int tid  = threadIdx.x + blockDim.x*blockIdx.x;

    if(tid<n) {
        v[tid] = value;
    }
}

template <typename T>
void fill_gpu(T *v, T value, int n) {
    auto block_dim = 192ul;
    auto grid_dim = n/block_dim + (n%block_dim ? 1 : 0);

    fill<T><<<grid_dim, block_dim>>>(v, value, n);
}

template <typename T>
void fill_random_ones(T* v, double probability, int n)
{
    probability = fmod(probability, 1); // ensure it is between 0 and 1;

    std::srand(std::time(nullptr));

    for (int i = 0; i < n; i++)
    {
        double rnd = ((double) rand() / (RAND_MAX));
        if (rnd > probability)
        {
            v[i] = 0;
        }
        else
        {
            v[i] = 0.2;
        }
    }
}

template <typename T>
void fill_hole(T* v, int n, int nx, int ny)
{
    for (int i = 0; i < n; i++)
    {
        int x = i%nx;
        int y = (i - x)/ny;

        if (x > 0.4*nx && x < 0.6*nx && y > 0.4*ny && y < 0.6*ny)
        {
            v[i] = 0;
        }
    }
}

void write_to_file(int nx, int ny, double* data) {
    {
        FILE* output = fopen("output.bin", "w");
        fwrite(data, sizeof(double), nx * ny, output);
        fclose(output);
    }

    std::ofstream fid("output.bov");
    fid << "TIME: 0.0" << std::endl;
    fid << "DATA_FILE: output.bin" << std::endl;
    fid << "DATA_SIZE: " << nx << " " << ny << " 1" << std::endl;;
    fid << "DATA_FORMAT: DOUBLE" << std::endl;
    fid << "VARIABLE: phi" << std::endl;
    fid << "DATA_ENDIAN: LITTLE" << std::endl;
    fid << "CENTERING: nodal" << std::endl;
    fid << "BRICK_SIZE: 1.0 1.0 1.0" << std::endl;
}