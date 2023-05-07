include("./LoadObj.jl")
using .LoadObj
using LinearAlgebra
using BenchmarkTools


const NULL_INTERSECTION::Vector{Float64} = [Inf, Inf, Inf]
function getHitLocation(start::Vector{Float64}, dir::Vector{Float64}, t::Float64)
    return start + dir * t

end


function triIntersect(triangle::Vector{Int64}, points::Vector{Vector{Float64}}, start::Vector{Float64}, dir::Vector{Float64})
    eps = 0.000001


    verticies = map((x) -> points[x], triangle)
    v1, v2, v3 = verticies
    edge1 = v2 - v1
    edge2 = v3 - v1

    pvec = dir × edge2
    det = edge1 ⋅ pvec

    if (abs(det) < eps)
        return false, NULL_INTERSECTION
    end

    inv_det = 1 / det
    tvec = start - v1
    u = (tvec ⋅ pvec) * inv_det

    if u < 0.0 || u > 1.0  # if not intersection
        return false, NULL_INTERSECTION
    end

    qvec = tvec × edge1
    v = dot(dir, qvec) * inv_det
    if v < 0.0 || u + v > 1.0  # if not intersection
        #  print('fail3')
        return false, NULL_INTERSECTION
    end

    t = (edge2 ⋅ qvec) * inv_det
    if t < eps
        #   print('fail4')
        return false, NULL_INTERSECTION
    end

    return true, [t, u, v]

end


struct HitInfo
    start::Vector{Float64}
    vec::Vector{Float64}
    t::Float64
    obj::Object
    tri::Int64
    didHit::Bool
    u::Float64
    v::Float64
end

const NULLHIT::HitInfo = HitInfo(Vector(), Vector(), 0, Object("null", Vector()), 0, false, 0, 0)

function checkIntersections(data::GeometryData, start::Vector{Float64}, ray::Vector{Float64})::HitInfo
    min_t = Inf
    u = 0.0
    v = 0.0
    #hitInfo = HitInfo([], [], 0, [], false, 0, 0)
    hit = false
    t = 0
    tri = 0
    obj = Object("null", Vector())
    for object in data.objects
        #for triangle::Vector{Int64} in data.triangles[object.triangles]
        for i in 1:length(data.triangles[object.triangles])
            didHit, vec = triIntersect(data.triangles[object.triangles][i], data.points, start, ray)
            if didHit && vec[1] < min_t
                min_t = vec[1]
                t = min_t
                tri = i #triangle
                hit = didHit
                u = vec[2]
                v = vec[3]
                obj = object
            end

        end
    end
    #println(obj)
    return HitInfo(start, ray, t, obj, tri, hit, u, v)
    #return start, ray, t, obj, tri, hit, u, v
end


function twobounce(data::GeometryData, start::Vector{Float64}, ray::Vector{Float64})::Tuple{HitInfo,HitInfo}
    result::HitInfo = checkIntersections(data, start, ray)


    nullVector = Vector()
    if !result.didHit
        return (result, NULLHIT)
    end
    newStart = getHitLocation(result.start, result.vec, result.t)

    n = data.points_n[geodata.triangles_n[2]][1]
    new_r = ray - n * ((2 * ray) ⋅ n / (norm(n) * norm(n)))

    result2 = checkIntersections(data, newStart, new_r)

    return result, result2

end

function calcTextureCoordinates(u::Float64, v::Float64, w::Float64, data::Vector{Vector{Float32}})
    coord = [w, u, v]
    #result = data ⋅ coord

    return w * data[1] + u * data[2] + v * data[3]
end

function writeToFile(file, data::GeometryData, result::Tuple{HitInfo,HitInfo})
    for i in 1:2
        hit = result[i]
        if !hit.didHit
            return
        else
            point_coords = calcTextureCoordinates(hit.u, hit.v, 1 - hit.u - hit.v, data.points_t[data.triangles_t[hit.tri]])
            write(file, "$(hit.obj.name)\t$i\t$(point_coords[1]),$(point_coords[2])\n")
        end
    end
end
function iterateStartVecs(data::GeometryData, n0, n)
    outFile = open("testOut.txt", "w")
    div = (n - n0) // 7500
    start = [0.0, 0.0, 0.0]
    for t in n0:n
        θ = rand() * π
        ϕ = rand() * 2π
        dir = [cos(ϕ) * sin(θ), sin(θ) * sin(ϕ), cos(θ)]
        res = twobounce(data, start, dir)
        #writeToFile(outFile, data, res)
    end


    close(outFile)


end



@time geodata = loadObj("./FourCubes.obj")

@time iterateStartVecs(geodata, 0, 10_000)