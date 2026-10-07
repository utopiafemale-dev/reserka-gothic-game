import PartySocket from "partysocket";
import type { ClientMessage, Player, ServerMessage, WorldState } from "./types";
type Handler=(m:ServerMessage)=>void;
const defaultWorld=():WorldState=>({startedAt:Date.now(),timeOffset:0,timeScale:1,paused:false,sharedEvents:[],storyFlags:[]});
export class Network {
  socket?:PartySocket; handler:Handler=()=>{}; localPlayers=new Map<string,Player>(); channel?:BroadcastChannel;
  constructor(public room:string,public player:Player){}
  connect(handler:Handler){
    this.handler=handler; const host=import.meta.env.VITE_PARTYKIT_HOST as string|undefined;
    if(host){ this.socket=new PartySocket({host,room:this.room}); this.socket.onopen=()=>this.send({type:"join",player:this.player}); this.socket.onmessage=e=>handler(JSON.parse(e.data)); this.socket.onerror=()=>handler({type:"error",message:"The room fell silent. Reconnecting…"}); }
    else { // Local zero-config transport makes multi-tab testing and offline play possible.
      this.channel=new BroadcastChannel(`kage-${this.room}`); this.channel.onmessage=e=>this.receiveLocal(e.data); this.localPlayers.set(this.player.id,this.player); this.channel.postMessage({type:"peer-join",player:this.player}); this.emitLocal();
    }
  }
  receiveLocal(m:any){ if(m.type==="peer-join"){this.localPlayers.set(m.player.id,m.player);this.channel?.postMessage({type:"peer-state",player:this.player});} if(m.type==="peer-state")this.localPlayers.set(m.player.id,m.player);if(m.type==="peer-left")this.localPlayers.delete(m.id);this.emitLocal(); }
  emitLocal(){this.handler({type:"state",players:[...this.localPlayers.values()],world:defaultWorld()});}
  send(m:ClientMessage){if(this.socket?.readyState===WebSocket.OPEN)this.socket.send(JSON.stringify(m)); else if(this.channel){if(m.type==="move")Object.assign(this.player,m);if(m.type==="event"){}this.localPlayers.set(this.player.id,this.player);this.channel.postMessage({type:"peer-state",player:this.player});this.emitLocal();}}
  close(){this.channel?.postMessage({type:"peer-left",id:this.player.id});this.channel?.close();this.socket?.close();}
}
export function validCode(code:string){return /^[A-Z]{4}$/.test(code);}
export function roomCode(random=Math.random){const chars="ABCDEFGHJKLMNPQRSTUVWXYZ";return Array.from({length:4},()=>chars[Math.floor(random()*chars.length)]).join("");}
