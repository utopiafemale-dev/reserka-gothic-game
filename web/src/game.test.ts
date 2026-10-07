import { describe,expect,it } from "vitest";
import { generateIdentity } from "./character";
import { roomCode,validCode } from "./network";
import { isBlocked,phaseAt,regions } from "./world";
import { availableTrialChoices } from "./events";
describe("KAGE systems",()=>{
 it("creates deterministic complete identities",()=>{const i=generateIdentity(()=>0);expect(i.archetype).toBe("Fallen Samurai");expect(i.burden).toBe("Guilt");expect(i.abilities.length).toBe(2)});
 it("generates and validates four letter rooms",()=>{expect(roomCode(()=>0)).toBe("AAAA");expect(validCode("KAGE")).toBe(true);expect(validCode("bad!")).toBe(false)});
 it("has connected playable regions",()=>{expect(Object.keys(regions)).toHaveLength(5);expect(regions.village.exits[0].to).toBe("bamboo");expect(isBlocked("village",0,0)).toBe(true)});
 it("cycles through narrative phases",()=>{expect(phaseAt(0)).toBe("DAY");expect(phaseAt(9)).toBe("DUSK");expect(phaseAt(13)).toBe("NIGHT");expect(phaseAt(18)).toBe("DAWN")});
 it("adapts trial choices to party roles",()=>{const identity=generateIdentity(()=>0);const choices=availableTrialChoices([{id:"1",name:"S",x:0,y:0,region:"river",direction:"down",moving:false,health:100,identity,color:"red"}]);expect(choices.some(c=>c.need==="Fallen Samurai")).toBe(true);expect(choices.some(c=>c.need==="Physician")).toBe(false)});
});
