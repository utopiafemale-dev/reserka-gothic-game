import type { Identity } from "./types";
const archetypes: Record<string,string[]> = {
  "Fallen Samurai":["Guard","Measured Strike"], "Shrine Keeper":["Ward","Spirit Lore"],
  "Exiled Monk":["Center","Purify"], Hunter:["Track","Snare"], Physician:["Mend","Diagnose"],
  Gravedigger:["Endure","Last Rites"], "Lost Pilgrim":["Wayfind","Listen"], "Cursed Heir":["Command","Blood Memory"],
  Outcast:["Vanish","Scavenge"], Wanderer:["Adapt","Flee"]
};
const burdens = ["Guilt","Fear","Grief","Pride","Paranoia","Cowardice","Loneliness","Obsession","Anger","Self-Doubt"];
const pick=<T>(a:T[], random=Math.random)=>a[Math.floor(random()*a.length)];
export function generateIdentity(random=Math.random):Identity {
  const archetype=pick(Object.keys(archetypes),random); const burden=pick(burdens,random);
  return {archetype,burden,seed:`${pick(["ash","bell","river","mask","cedar"],random)}-${Math.floor(random()*9999)}`,abilities:archetypes[archetype],wisdom:1+Math.floor(random()*3),courage:1+Math.floor(random()*3),compassion:1+Math.floor(random()*3),corruption:0,deaths:0,flags:[],memories:[],relationships:{},encounters:[]};
}
const KEY="kage-character-v1";
export function loadIdentity():Identity { try { const raw=localStorage.getItem(KEY); if(raw) return {...generateIdentity(),...JSON.parse(raw)}; } catch{} return generateIdentity(); }
export function saveIdentity(value:Identity){ localStorage.setItem(KEY,JSON.stringify(value)); }
