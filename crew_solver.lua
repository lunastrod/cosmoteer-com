--[[
    Modification by LunastroD to add it to the Cosmoteer bot, 2024-05-05
]]--

--[[
	Code to analytically claculate the crew requirements for a stretch of walkway in cosmoteer
	Author: StuffPhoton

	each iteration, it claculates the probablity of a tile having crew via the congestion values
	from the last iteration by assuming a random distribution of crew.

	Testing shows that this seem to converge to double precision limits within 20-30 iterations,
	this program runs it for 50 iterations. which should be good enough
]]--








--[[
	world dictionary:
		space - impassible
		p - producer. produces infinite resources. 
		b - bogus producer. produces infinite resources with no pathing cost
		c - default consumer. consumes resources at consumerRate
		1-9 - custom consumer. consumers resources at consumerRates[num]
		. - corridor. 
		; - room. 
		^ v < > - conveyors
]]


-- =========== CONSTANTS ===========
-- universal parameters

-- Yes, you'll have to manually set the module in the src every time
local worlds = {
	{
    "1.p;  ",
    "   .  ",
    "  1.2 ",
	}
}

local pathOpacity = 1
local pathWidth = 3
local printCrewBreakdown = true
local crewProbWatch = "1"
local onlyWatchPowered = true
local printCrewProb = true

local defaultConsumerRate = 0.89 / 3
local batterySize = 1
local consumerRates = {
	["1"] = 1.60,
	["2"] = 1.60/2,
	["3"] = 1.62,
	["4"] = 0,
	["5"] = 0,
	["6"] = 0,
	["7"] = 0,
	["8"] = 0,
	["9"] = 0,
}
	for k, v in pairs(consumerRates) do consumerRates[k] = v / batterySize end

local roomPathCost = 1/0.5
local cooridoorPathCost = 1/1
local conveyorForwardPathCost = 1/2
local conveyorSidePathCost = 1/0.75
local conveyorBackPathCost = 1/0.25
local roomCongestion = 0.3
local cooridoorCongestion = 0.5

local pickupTime = 1
local crewSpeed = 3.2

local cost = 0
local huge = 100000000

local tilePathCosts = {
	-- example : {right, left, up, down},
	[" "] = {huge, huge, huge, huge},
	["p"] = {roomPathCost, roomPathCost, roomPathCost, roomPathCost},
	["b"] = {0, 0, 0, 0},
	["c"] = {roomPathCost, roomPathCost, roomPathCost, roomPathCost},
	["."] = {cooridoorPathCost, cooridoorPathCost, cooridoorPathCost, cooridoorPathCost},
	[";"] = {roomPathCost, roomPathCost, roomPathCost, roomPathCost},
	["^"] = {conveyorSidePathCost, conveyorSidePathCost, conveyorForwardPathCost, conveyorBackPathCost},
	["v"] = {conveyorSidePathCost, conveyorSidePathCost, conveyorBackPathCost, conveyorForwardPathCost},
	["<"] = {conveyorBackPathCost, conveyorForwardPathCost, conveyorSidePathCost, conveyorSidePathCost},
	[">"] = {conveyorForwardPathCost, conveyorBackPathCost, conveyorSidePathCost, conveyorSidePathCost},
}

local tileCongestionCosts = {
	[" "] = 0,
	["p"] = roomCongestion,
	["b"] = 0,
	["c"] = roomCongestion,
	["."] = cooridoorCongestion,
	[";"] = roomCongestion,
	["^"] = cooridoorCongestion,
	["v"] = cooridoorCongestion,
	["<"] = cooridoorCongestion,
	[">"] = cooridoorCongestion,
}

local i
for i = 1, 9 do
	tilePathCosts[""..i] = tilePathCosts["c"]
	tileCongestionCosts[""..i] = tileCongestionCosts["c"]
end

local function straightLineBonus(emptyProb)
	local crewProb = 1 - emptyProb
	crewProb = math.max((crewProb - 0.5) * 2, 0)
	return 1 - crewProb
end

local tileSprites = {}
local tileSize = 32
local spriteParams = {dpiscale = 64/tileSize}
local spriteFolder = "Assets/"

local pathColors = {
	{1,   0,   0  },
	{0,   1,   0  },
	{0,   0,   1  },
	{1,   1,   0  },
	{0,   1,   1  },
	{1,   0,   1  },
}
local k
for k=1, 6 do
	pathColors[#pathColors+1] = {pathColors[k][1] * 0.5, pathColors[k][2] * 0.5, pathColors[k][3] * 0.5}
	pathColors[#pathColors+1] = {1 - pathColors[k][1] * 0.5, 1 - pathColors[k][2] * 0.5, 1 - pathColors[k][3] * 0.5}
end


local world, worldHeight, worldWidth
local totalCrewReqs = 0
local crewReqs = {}
local crewProbs = {}

local function initWorld(worldNum)
	world = worlds[worldNum]
	worldHeight = #world
	worldWidth = string.len(world[1])
end

local consumers = {}


-- =========== WORLD SETUP ===========
-- this is responsible for handling crew pathing and world setup


local function isPosInBounds(x, y)
	return x > 0 and y > 0 and x <= worldWidth and y <= worldHeight
end

local function getTileByCoords(x, y)
	return string.sub(world[worldHeight - y + 1], x, x)
end


local function iterateThroughWorld(func)
	local x, y
	for x=1, worldWidth do
		for y=1, worldHeight do
			func(getTileByCoords(x, y), x, y)
		end
	end
end


local function registerConsumer(char, x, y)
	if char ~= "c" and not consumerRates[char] then
		return
	end

	local consumerData = {}
	consumers[#consumers+1] = consumerData

	consumerData.x = x
	consumerData.y = y
	consumerData.pathToProducer = {}
	consumerData.pathFromProducer = {}
	consumerData.crewReq = 0
	consumerData.rate = consumerRates[char] or defaultConsumerRate
	consumerData.char = char
end



local pathfinderQueue = {}
local pathfinderMap = {}

local function updatePathfinderNeighbor(neighborTile, newDistance, parent)
	if not neighborTile.explored and neighborTile.distance > newDistance then
		neighborTile.distance = newDistance
		if neighborTile.queuePos then
			neighborTile.queuePos.distance = newDistance
		else 
			pathfinderQueue[#pathfinderQueue+1] = {distance = newDistance, x = neighborTile.x, y = neighborTile.y}
		end
		neighborTile.parent = parent
	end
end

local function getShortestPath(startX, startY, targetFilter)
	-- init pathfinder data
	pathfinderQueue = {}
	pathfinderMap = {}
	for x=1, worldWidth do
		pathfinderMap[x] = {}
		for y=1, worldHeight do
			pathfinderMap[x][y] = {x = x, y = y, explored = false, distance = math.huge, parent = nil, queuePos = nil}
		end
	end

	pathfinderQueue[1] = {distance = 0, x = startX, y = startY}
	pathfinderMap[startX][startY] = {x = startX, y = startY, explored = false, distance = 0, parent = "start", queuePos = pathfinderQueue[1]}

	-- begin exploration
	while not targetFilter(pathfinderQueue[1]) do
		local x = pathfinderQueue[1].x
		local y = pathfinderQueue[1].y
		local distance = pathfinderQueue[1].distance
		
		pathfinderMap[x][y].explored = true
		
		if isPosInBounds(x+1, y) then
			local cost = (tilePathCosts[getTileByCoords(x, y)][1] + tilePathCosts[getTileByCoords(x+1, y)][1]) / 2
			updatePathfinderNeighbor(pathfinderMap[x+1][y], distance+cost, pathfinderMap[x][y])
		end
		if isPosInBounds(x-1, y) then
			local cost = (tilePathCosts[getTileByCoords(x, y)][2] + tilePathCosts[getTileByCoords(x-1, y)][2]) / 2
			updatePathfinderNeighbor(pathfinderMap[x-1][y], distance+cost, pathfinderMap[x][y])
		end
		if isPosInBounds(x, y+1) then
			local cost = (tilePathCosts[getTileByCoords(x, y)][3] + tilePathCosts[getTileByCoords(x, y+1)][3]) / 2
			updatePathfinderNeighbor(pathfinderMap[x][y+1], distance+cost, pathfinderMap[x][y])
		end
		if isPosInBounds(x, y-1) then
			local cost = (tilePathCosts[getTileByCoords(x, y)][4] + tilePathCosts[getTileByCoords(x, y-1)][4]) / 2
			updatePathfinderNeighbor(pathfinderMap[x][y-1], distance+cost, pathfinderMap[x][y])
		end
		
		table.remove(pathfinderQueue, 1)

		table.sort(pathfinderQueue, function (tile1, tile2) return tile1.distance < tile2.distance end )
	end

	-- now, the first element in pathfinderQueue is the closest target.
	-- construct the path from back-tracing
	local reversedPath = {}
	local path = {}

	local tile = pathfinderMap[pathfinderQueue[1].x][pathfinderQueue[1].y]
	while tile ~= "start" do
		reversedPath[#reversedPath+1] = {x = tile.x, y = tile.y, inDir = nil, outDir = nil}
		tile = tile.parent
	end

	local i
	for i=1, #reversedPath do
		path[#reversedPath - i + 1] = reversedPath[i]
	end


	-- add in the directions in this path
	for i=1, #path - 1 do
		local tile1 = path[i]
		local tile2 = path[i+1]
		local dir
		if tile2.x == tile1.x + 1 then
			dir = 1
		elseif tile2.x == tile1.x - 1 then
			dir = 2
		elseif tile2.y == tile1.y + 1 then
			dir = 3
		elseif tile2.y == tile1.y - 1 then
			dir = 4
		else
			print("[Error]: Unrecognised direction.")
		end

		tile1.outDir = dir
		tile2.inDir = dir
	end

	return path, pathfinderQueue[1]
end


local function targetProducer(tile)
	return getTileByCoords(tile.x, tile.y) == "p" or getTileByCoords(tile.x, tile.y) == "b"
end
local targetX, targetY
local function targetPos(tile)
	return tile.x == targetX and tile.y == targetY
end


-- =========== SOLVER ===========
-- iterative congestion solver


local congestionMap

function initCongestionMap()
	congestionMap = {}
	crewProbs = {}
	local x, y
	for x = 1, worldWidth do
		congestionMap[x] = {}
		crewProbs[x] = {}
		for y = 1, worldHeight do
			congestionMap[x][y] = {emptyProb = 1, nextEmptyProb = 1, isStraight = true, inDir = nil}
			crewProbs[x][y] = 0
		end
	end

	local i, n
	for i = 1, #consumers do
		-- Get total path length
		local consumer = consumers[i]
		for n = 1, #consumer.pathToProducer do
			local segment = consumer.pathToProducer[n]
			congestionMap[segment.x][segment.y].inDir = congestionMap[segment.x][segment.y].inDir or segment.inDir
			if congestionMap[segment.x][segment.y].inDir ~= segment.inDir then
				congestionMap[segment.x][segment.y].isStraight = false
			end
		end
		for n = 1, #consumer.pathFromProducer do
			local segment = consumer.pathFromProducer[n]
			congestionMap[segment.x][segment.y].inDir = congestionMap[segment.x][segment.y].inDir or segment.inDir
			if congestionMap[segment.x][segment.y].inDir ~= segment.inDir then
				congestionMap[segment.x][segment.y].isStraight = false
			end
		end
	end
end


local function getPathSegmentLength(segment)
	local length = 0
	local x = segment.x
	local y = segment.y
	if segment.inDir then
		local emptyProb = congestionMap[x][y].emptyProb
		if congestionMap[x][y].isStraight then
			emptyProb = straightLineBonus(emptyProb)
		end
		length = length + (tilePathCosts[getTileByCoords(x, y)][segment.inDir] / (1 - (tileCongestionCosts[getTileByCoords(x, y)] * (1 - emptyProb))))
	end
	--assume the path always points in-bounds
	if segment.outDir then
		local outTo
		if segment.outDir == 1 then
			outTo = congestionMap[x+1][y]
		elseif segment.outDir == 2 then
			outTo = congestionMap[x-1][y]	
		elseif segment.outDir == 3 then
			outTo = congestionMap[x][y+1]
		elseif segment.outDir == 4 then
			outTo = congestionMap[x][y-1]
		end
		
		local emptyProb = outTo.emptyProb
		if outTo.isStraight then
			emptyProb = straightLineBonus(emptyProb)
		end
		length = length + (tilePathCosts[getTileByCoords(x, y)][segment.outDir] / (1 - (tileCongestionCosts[getTileByCoords(x, y)] * (1 - emptyProb))))
	end

	return length / 2
end


function congestionSolverIteration()
	local i
	totalCrewReqs = 0
	local x, y
	for x = 1, worldWidth do
		for y = 1, worldHeight do
			crewProbs[x][y] = 0
		end
	end
	for i = 1, #consumers do
		-- Get total path length and crew reqs
			local consumer = consumers[i]
			local pathLength = 0
			local n
			for n = 1, #consumer.pathToProducer do
				pathLength = pathLength + getPathSegmentLength(consumer.pathToProducer[n])
			end
			for n = 1, #consumer.pathFromProducer do
				pathLength = pathLength + getPathSegmentLength(consumer.pathFromProducer[n])
			end
			
			pathLength = pathLength + crewSpeed * pickupTime
			local crewReq = consumer.rate * pathLength / crewSpeed

			totalCrewReqs = totalCrewReqs + crewReq
			crewReqs[i] = crewReq
		
		-- apply congestion
		local function applyCongestion(path, toProducer)
			local n
			for n=1, #path do
				local segment = path[n]
				local frac =  (getPathSegmentLength(segment) + ((toProducer and ((n == #consumer.pathToProducer and crewSpeed * pickupTime) or 0)) or 0)) / pathLength
				local noCrewProb = (1 - frac) ^ crewReq
				congestionMap[segment.x][segment.y].nextEmptyProb = congestionMap[segment.x][segment.y].nextEmptyProb * noCrewProb
				if (consumer.char == crewProbWatch or not crewProbWatch) and (onlyWatchPowered and not toProducer) then
					crewProbs[segment.x][segment.y] = crewProbs[segment.x][segment.y] + (frac * crewReq)
				end
			end
		end
		applyCongestion(consumer.pathFromProducer, false)
		applyCongestion(consumer.pathToProducer, true)
	end

	-- now push nextEmptyProb up
	for x = 1, worldWidth do
		for y = 1, worldHeight do
			congestionMap[x][y].emptyProb = congestionMap[x][y].nextEmptyProb
			congestionMap[x][y].nextEmptyProb = 1
		end
	end
	return totalCrewReqs
end

function accept_args()
    -- Check if there are at least 11 command-line arguments
    if #arg < 11 then
        print("Usage: lua52 crew_solver.lua <worlds> <batterySize> <consumerRate1> <consumerRate2> ... <consumerRate9>")
        os.exit(1)
    end

    -- Read the first command-line argument (the string)
    worlds = table.concat(arg, " ", 1, 1)

    -- Read the second command-line argument (the number)
    batterySize = tonumber(arg[2]) or 0
    if batterySize == nil then
        print("Invalid battery size:", arg[2])
        os.exit(1)
    end

    -- Read the next 9 command-line arguments (the numbers)
    consumerRates = {}
    for i = 3, 11 do
        local rate_str = arg[i]
        local rate = tonumber(rate_str)
        if rate == nil then
            print("Invalid consumer rate:", rate_str)
            os.exit(1)
        end
        consumerRates[tostring(i - 2)] = rate
    end

    -- Use the parsed arguments in your script
    print("Worlds:", worlds)
    print("Battery Size:", batterySize)
    print("Consumer Rates:")
    for k, v in pairs(consumerRates) do
        print("  Consumer Rate "..k..":", v)
    end
end

function main()
    accept_args()
    initWorld(1)
    iterateThroughWorld(registerConsumer)
    local producer
    local i
    for i=1, #consumers do
    	consumers[i].pathToProducer, producer = getShortestPath(consumers[i].x, consumers[i].y, targetProducer)
    	targetX, targetY = consumers[i].x, consumers[i].y
    	consumers[i].pathFromProducer, _ = getShortestPath(producer.x, producer.y, targetPos)
    end
    initCongestionMap()
    totalCrewReqs=0
    for i = 1, 50 do -- haha computer goes brrrrrrr
    	totalCrewReqs=congestionSolverIteration()
    	print("Iteration "..i.." of crew solver, crew required: "..totalCrewReqs)
    end
    print("Crew required: "..totalCrewReqs)
end

main()


-- =========== GUI ===========
-- LOVE graphics
--[[

function love.load()
	initWorld(1)
	iterateThroughWorld(registerConsumer)

	local i
	tileSprites["p"] = love.graphics.newImage(spriteFolder.."producer.png", spriteParams)
	tileSprites["b"] = love.graphics.newImage(spriteFolder.."bogusProducer.png", spriteParams)
	tileSprites["c"] = love.graphics.newImage(spriteFolder.."consumer.png", spriteParams)
	for i = 0, 9 do tileSprites[""..i] = tileSprites["c"] end
	tileSprites["."] = love.graphics.newImage(spriteFolder.."corridor.png", spriteParams)
	tileSprites[";"] = love.graphics.newImage(spriteFolder.."room.png", spriteParams)
	tileSprites["^"] = love.graphics.newImage(spriteFolder.."conveyorUp.png", spriteParams)
	tileSprites["v"] = love.graphics.newImage(spriteFolder.."conveyorDown.png", spriteParams)
	tileSprites["<"] = love.graphics.newImage(spriteFolder.."conveyorLeft.png", spriteParams)
	tileSprites[">"] = love.graphics.newImage(spriteFolder.."conveyorRight.png", spriteParams)

	local producer
	local i
	for i=1, #consumers do
		consumers[i].pathToProducer, producer = getShortestPath(consumers[i].x, consumers[i].y, targetProducer)
		targetX, targetY = consumers[i].x, consumers[i].y
		consumers[i].pathFromProducer, _ = getShortestPath(producer.x, producer.y, targetPos)
	end

	initCongestionMap()
	for i = 1, 50 do -- haha computer goes brrrrrrr
		congestionSolverIteration(i)
	end
end


local xOffset, yOffset
local function renderTile(tile, x, y)
	if tile ~= " " then
		love.graphics.draw(tileSprites[tile], (xOffset + x) * tileSize, (yOffset + worldHeight - y) * tileSize)
		if printCrewProb and crewProbs[x][y] ~= 0 then
			love.graphics.print(math.ceil(crewProbs[x][y]*100)/100, (xOffset + x) * tileSize, (yOffset + worldHeight - y) * tileSize+20, 0, 0.8, 0.8, 0, 0)
		end
	end
end

function renderPath(path, offset)
	local i
	for i=1, #path-1 do
		love.graphics.line(
			(xOffset + path[i  ].x + 0.5) * tileSize + offset,
			(yOffset + worldHeight - path[i  ].y + 0.5) * tileSize + offset,
			(xOffset + path[i+1].x + 0.5) * tileSize + offset,
			(yOffset + worldHeight - path[i+1].y + 0.5) * tileSize + offset
		)
	end
end


function love.draw()
	xOffset = 1
	yOffset = 1
	love.graphics.setColor(1, 1, 1, 1)
    iterateThroughWorld(renderTile)

	local i
	love.graphics.setLineWidth(pathWidth)
	for i=1, #consumers do
		local color = pathColors[i]
		local offset = (i - #consumers/2) * pathWidth

		love.graphics.setColor(color[1], color[2], color[3], pathOpacity)
		renderPath(consumers[i].pathFromProducer, offset)
		love.graphics.setColor(color[1]/1.6, color[2]/1.6, color[3]/1.6, pathOpacity)
		renderPath(consumers[i].pathToProducer, offset)
		
		
		love.graphics.setColor(1, 1, 1, 1)
		love.graphics.print(i, (xOffset + consumers[i].x) * tileSize, (yOffset + worldHeight - consumers[i].y) * tileSize, 0, 1, 1, 0, 0)
	end
	
	love.graphics.setColor(1, 1, 1, 1)
	love.graphics.print("Total Crew Required: "..totalCrewReqs, 0, 0, 0, 1, 1, 0, 0)
	
	love.graphics.print("== Crew Breakdown == ", 0, (yOffset + worldHeight) * tileSize, 0, 1, 1, 0, 0)
	for i=1, #crewReqs do
		love.graphics.print("Consumer #"..i.." requires "..crewReqs[i].." crew", 20, (yOffset + worldHeight) * tileSize + i * 20, 0, 1, 1, 0, 0)
	end
	love.graphics.print("Total Crew Required: "..totalCrewReqs, 0, (yOffset + worldHeight) * tileSize + (#crewReqs+1) * 20, 0, 1, 1, 0, 0)
	
end
]]--