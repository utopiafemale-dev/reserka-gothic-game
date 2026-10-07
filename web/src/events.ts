import type { Identity, Phase, Player, RegionId } from "./types";
export interface HorrorEvent {id:string;region:RegionId;stage:"PRIVATE"|"BLEEDING"|"SHARED";text:string;visible:(i:Identity,p:Phase,shared:string[])=>boolean}
export const horrorEvents:HorrorEvent[]=[
 {id:"watcher",region:"bamboo",stage:"PRIVATE",text:"A woman stands between the bamboo. She has your posture.",visible:(i)=>["Guilt","Paranoia","Grief"].includes(i.burden)||i.deaths>0},
 {id:"watcher-shared",region:"bamboo",stage:"SHARED",text:"Everyone can see her now.",visible:(_i,p,s)=>p==="NIGHT"&&s.includes("watcher-shared")}
];
export const trial={id:"wounded-spirit",region:"river" as RegionId,title:"The Wounded Guardian",setup:"A fox-masked spirit shields a bundle beside the river.",choices:[{label:"Raise your weapon",need:"Fallen Samurai",effect:"courage"},{label:"Read the ward",need:"Shrine Keeper",effect:"wisdom"},{label:"Treat its wound",need:"Physician",effect:"compassion"},{label:"Wait and listen",need:null,effect:"wisdom"}]};
export function availableTrialChoices(players:Player[]){return trial.choices.filter(c=>!c.need||players.some(p=>p.identity.archetype===c.need));}
