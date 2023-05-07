using CUDA
using BenchmarkTools



function vadd!(c, a, b)
    for i in 1:length(a)
        @inbounds c[i] = a[i] + b[i]
    end
end

function vaddGPU!(c, a, b)
    i = threadIdx().x + (blockIdx().x - 1) * blockDim().x
    if i <= length(a)
        @inbounds c[i] = a[i] + b[i]

    end
    return nothing
end

A = CuArray(ones(2^20))
B = CuArray(ones(2^20) * 0.2)
C = CuArray(similar(A))
@btime $C .= $A .+ $B
nthreads = 1024
numblocks = cld(length(A), nthreads)

@btime CUDA.@sync @cuda threads = nthreads blocks = numblocks vaddGPU!($C, $A, $B)
