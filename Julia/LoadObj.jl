using FileIO
module LoadObj

export GeometryData, loadObj, Object


struct Object
    name::String
    triangles::Vector{Int64}
end


struct GeometryData
    points::Vector{Vector{Float64}}
    points_t::Vector{Vector{Float32}}
    triangles::Vector{Vector{Int64}}
    triangles_t::Vector{Vector{Int64}}
    objects::Vector{Object}
end

#Load obj file as vectors
function loadObj(file::String)
    points = Vector{Vector{Float64}}()
    points_t = Vector{Vector{Float32}}()
    triangles = Vector{Vector{Int64}}()
    triangles_t = Vector{Vector{Int64}}()
    objects = Vector{Object}()

    currentObject::Object = Object("", Vector())
    for line in eachline(file)
        if isempty(line) || line[1] == "#"
            continue
        end
        parts = split(line, " ")

        if parts[1] == "o"
            if length(currentObject.triangles) !== 0
                push!(objects, currentObject)
            end
            currentObject = Object(parts[2], Vector{Int64}())
        elseif parts[1] == "v"
            vec = map(x -> parse(Float64, x), parts[2:end])
            push!(points, vec)
        elseif parts[1] == "vt"
            vec = map(x -> parse(Float32, x), parts[2:end])
            push!(points_t, vec)
        elseif parts[1] == "f"
            triangle::Vector{Int64} = Vector()
            triangle_t::Vector{Int64} = Vector()

            for point in parts[2:end]
                indicies = split(point, "/")
                index = parse(Int, indicies[1])
                textureIndex = parse(Int, indicies[2])
                push!(triangle, index)
                push!(triangle_t, textureIndex)
            end
            push!(triangles, triangle)
            push!(triangles_t, triangle_t)
            push!(currentObject.triangles, length(triangles))
        end
    end
    return GeometryData(points, points_t, triangles, triangles_t, objects)
    #return objects, points, points_t, triangles, triangles_t
end

end

#=
println("Object load")
data = loadObj("./FourCubes.obj")
println(data.objects)
=#

