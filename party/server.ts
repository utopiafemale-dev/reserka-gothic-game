import type * as Party from "partykit/server";
import type { ClientMessage, Player, ServerMessage, WorldState } from "../web/src/types";
const clean=(s:string,n=24)=>s.replace(/[^a-zA-Z0-9 _-]/g,"").slice(0,n);
export default class KageServer implements Party.Server {
 players=new Map<string,Player>(); world:WorldState={startedAt:Date.now(),timeOffset:0,timeScale:1,paused:false,sharedEvents:[],storyFlags:[]};
 constructor(readonly room:Party.Room){}
 onConnect(conn:Party.Connection){conn.send(JSON.stringify(this.state()));}
 onMessage(raw:string,sender:Party.Connection){let m:ClientMessage;try{m=JSON.parse(raw)}catch{return sender.send(JSON.stringify({type:"error",message:"Malformed message"}))}if(!m||typeof m.type!=="string")return;
  if(m.type==="join"&&this.players.size<8){const p=m.player;if(!p||typeof p.id!=="string"||!Number.isInteger(p.x)||!Number.isInteger(p.y))return;this.players.set(sender.id,{...p,id:sender.id,name:clean(p.name)});}
  const p=this.players.get(sender.id);if(!p)return;if(m.type==="move"&&Number.isInteger(m.x)&&Number.isInteger(m.y)&&Math.abs(m.x-p.x)+Math.abs(m.y-p.y)<=1){Object.assign(p,{x:m.x,y:m.y,region:m.region,direction:m.direction,moving:true});}if(m.type==="event"&&!this.world.sharedEvents.includes(clean(m.id)))this.world.sharedEvents.push(clean(m.id));if(m.type==="damage")p.health=Math.max(0,p.health-Math.min(25,Math.max(0,m.amount)));this.broadcast(); }
 onClose(conn:Party.Connection){this.players.delete(conn.id);this.room.broadcast(JSON.stringify({type:"player-left",id:conn.id} satisfies ServerMessage));this.broadcast();}
 state():ServerMessage{return {type:"state",players:[...this.players.values()],world:this.world}}
 broadcast(){this.room.broadcast(JSON.stringify(this.state()));}
}
