using FileIO

function objLoad(f::String)
    file = open(f)
    lines = readlines(file)

    verticies = []
    objects = []
    triangles = []
    normals = []
    texture_verticies = []
    curObject:string = nothing
    for line in lines
        if (line[1] == 'o')
            println(line)

        elseif (line[1] == 'v' && line[2] == ' ')
            println("push")
            spt = split(line, " ")
            push!(verticies, Vector{Float64}(map(Float64, spt)))
        end

    end
    return verticies

end
println("Object load")
println(objLoad("./FourCubes.obj"))
