extends RefCounted

# Platforms use x/y/width/height. Enemy positions mark their feet.
const STAGES: Array = [
 {"name":"The Castle Approach", "width":2400, "background":"castle", "music":"castle",
 "tint":Color(0.65,0.6,0.78), "stone":Color(0.2,0.15,0.29),
 "platforms":[Rect2(0,480,2400,60),Rect2(240,380,230,22),Rect2(570,305,220,22),Rect2(920,375,230,22),Rect2(1300,290,220,22),Rect2(1680,365,240,22),Rect2(2040,300,220,22)],
 "enemies":[["skull",Vector2(410,340)],["skull",Vector2(720,260)],["hound",Vector2(1080,480)],["skull",Vector2(1440,250)],["demon",Vector2(1840,480)]],
 "hazards":[], "heals":[Vector2(680,285),Vector2(2110,280)]},
 {"name":"The Drowned Swamp", "width":2800, "background":"swamp", "music":"swamp",
 "tint":Color(0.65,0.85,0.7), "stone":Color(0.12,0.25,0.19),
 "platforms":[Rect2(0,480,2800,60),Rect2(280,370,200,22),Rect2(580,300,200,22),Rect2(920,375,190,22),Rect2(1210,280,210,22),Rect2(1580,370,210,22),Rect2(1910,290,230,22),Rect2(2300,370,230,22)],
 "enemies":[["hound",Vector2(430,480)],["skull",Vector2(680,250)],["demon",Vector2(1040,480)],["skull",Vector2(1330,230)],["hound",Vector2(1730,480)],["skull",Vector2(2020,245)],["demon",Vector2(2440,480)]],
 "hazards":[Rect2(520,458,70,22),Rect2(1450,458,80,22),Rect2(2170,458,70,22)], "heals":[Vector2(990,355),Vector2(2010,270)]},
 {"name":"The Hollow Caverns", "width":3000, "background":"cavern", "music":"castle",
 "tint":Color(0.65,0.65,0.95), "stone":Color(0.13,0.17,0.3),
 "platforms":[Rect2(0,480,650,60),Rect2(760,480,680,60),Rect2(1550,480,620,60),Rect2(2290,480,710,60),Rect2(300,365,200,22),Rect2(580,300,250,22),Rect2(1030,355,230,22),Rect2(1340,290,270,22),Rect2(1810,350,230,22),Rect2(2100,285,260,22),Rect2(2520,355,220,22)],
 "enemies":[["hound",Vector2(440,480)],["skull",Vector2(720,250)],["demon",Vector2(1140,480)],["skull",Vector2(1460,245)],["hound",Vector2(1930,480)],["skull",Vector2(2220,245)],["demon",Vector2(2650,480)]],
 "hazards":[Rect2(890,458,80,22),Rect2(1680,458,80,22),Rect2(2390,458,80,22)], "heals":[Vector2(1130,335),Vector2(2220,265)]},
 {"name":"The Moonlit Graveyard", "width":2600, "background":"graveyard", "music":"battle",
 "tint":Color(0.85,0.55,0.6), "stone":Color(0.27,0.12,0.18),
 "platforms":[Rect2(0,480,2600,60),Rect2(270,365,220,22),Rect2(620,295,220,22),Rect2(1000,365,230,22),Rect2(1430,330,230,22),Rect2(1830,355,200,22),Rect2(2190,355,180,22)],
 "enemies":[["demon",Vector2(440,480)],["hound",Vector2(800,480)],["skull",Vector2(1110,300)],["demon",Vector2(1500,480)],["warden",Vector2(2120,480)]],
 "hazards":[Rect2(540,458,70,22),Rect2(1280,458,70,22)], "heals":[Vector2(1530,310),Vector2(2290,335)]}
]
