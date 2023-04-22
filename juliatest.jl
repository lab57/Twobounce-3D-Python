using BenchmarkTools
BenchmarkTools.DEFAULT_PARAMETERS.samples = 1
function main(shouldPrint)
    total = 1
    p = 0
    N = 100_000_000

    for i in 1:N
        total = total + i
        if i % (N / 20) == 0 && shouldPrint
            println("$p%")
            p += 5
        end
    end
end

main(false)
@time main(true)
