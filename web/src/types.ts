export type Direction = "up" | "down" | "left" | "right";
export type Phase = "DAY" | "DUSK" | "NIGHT" | "DAWN";
export type RegionId = "village" | "bamboo" | "river" | "shrine" | "woods";
export interface Identity { archetype:string; burden:string; seed:string; abilities:string[]; wisdom:number; courage:number; compassion:number; corruption:number; deaths:number; flags:string[]; memories:string[]; relationships:Record<string,number>; encounters:string[] }
export interface Player { id:string; name:string; x:number; y:number; region:RegionId; direction:Direction; moving:boolean; health:number; identity:Identity; color:string }
export interface WorldState { startedAt:number; timeOffset:number; timeScale:number; paused:boolean; sharedEvents:string[]; storyFlags:string[] }
export type ClientMessage = {type:"join"; player:Player}|{type:"move"; x:number;y:number;region:RegionId;direction:Direction}|{type:"event"; id:string}|{type:"damage"; amount:number};
export type ServerMessage = {type:"state"; players:Player[];world:WorldState}|{type:"error";message:string}|{type:"player-left";id:string};
