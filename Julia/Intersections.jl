include("./LoadObj.jl")
using .LoadObj
using LinearAlgebra



function triIntersect(triangle::Vector{Int64}, points::Vector{Vector{Float64}}, start::Vector{Float64}, dir::Vector{Float64})
    null_intersection::Vector{Float64} = [Inf, Inf, Inf]
    eps = 0.000001


    verticies = map((x) -> points[x], triangle)
    v1, v2, v3 = verticies
    edge1 = v2 - v1
    edge2 = v3 - v1

    pvec = dir × edge2
    det = edge1 ⋅ pvec

    if (abs(det) < eps)
        return false, null_intersection
    end

    inv_det = 1 / det
    tvec = start - v1
    u = (tvec ⋅ pvec) * inv_det

    if u < 0.0 || u > 1.0  # if not intersection
        return false, null_intersection
    end

    qvec = tvec × edge1
    v = dot(dir, qvec) * inv_det
    if v < 0.0 || u + v > 1.0  # if not intersection
        #  print('fail3')
        return false, null_intersection
    end

    t = (edge2 ⋅ qvec) * inv_det
    if t < eps
        #   print('fail4')
        return false, null_intersection
    end

    return true, [t, u, v]

end


struct HitInfo
    start::Vector{Float64}
    vec::Vector{Float64}
    t::Float64
    tri::Vector{Int64}
    didHit::Bool
    u::Float64
    v::Float64
end

function checkIntersections(data::GeometryData, start::Vector{Float64}, ray::Vector{Float64})
    min_t = Inf
    u = 0.0
    v = 0.0
    #hitInfo = HitInfo([], [], 0, [], false, 0, 0)
    hit = false
    t = 0
    tri = []
    obj = 0
    for object in data.objects
        for triangle::Vector{Int64} in data.triangles[object.triangles]
            didHit, vec = triIntersect(triangle, data.points, start, ray)
            if didHit && vec[1] < min_t
                min_t = vec[1]
                t = min_t
                tri = triangle
                hit = didHit
                u = vec[2]
                v = vec[3]
                obj = object
            end

        end
    end
    return start, ray, t, obj, tri, hit, u, v
end


function twobounce(data::GeometryData, start::Vector{Float64}, ray::Vector{Float64})
    _, _, t, _, didHit, u, v = checkIntersections(data, start, ray)
    if !hit
        return result, false
    end
end
geodata = loadObj("./FourCubes.obj")
println("Loaded")
triIntersect(geodata.triangles[1], geodata.points, [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
checkIntersections(geodata, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])