const $=id=>document.getElementById(id);let token=sessionStorage.getItem("formaAdminToken")||"";$("token").value=token;
function headers(){return {"Authorization":`Bearer ${token}`,"Content-Type":"application/json"}}
function notice(message,bad=false){$("notice").textContent=message;$("notice").style.background=bad?"#f5e1dc":"#e4e8d9";$("notice").style.color=bad?"#873f32":"#475632"}
async function api(path,options={}){const r=await fetch(path,{...options,headers:{...headers(),...(options.headers||{})}});if(!r.ok){let msg=`Request failed (${r.status})`;try{msg=(await r.json()).detail||msg}catch{}throw new Error(msg)}return r.json()}
function safe(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
async function refresh(){if(!token){notice("Enter the admin token and select Connect.");return}try{const [s,e]=await Promise.all([api("/api/admin/analytics/summary"),api("/api/admin/analytics/events?limit=50")]);$("total").textContent=s.total_visits;$("unique").textContent=s.unique_ips;$("simulated").textContent=s.simulated_visits;
const max=Math.max(1,...s.countries.map(x=>x.visits));$("countries").innerHTML=s.countries.length?s.countries.map(x=>`<div class="country-row"><div>${safe(x.country)}<div class="bar"><i style="width:${Math.round(x.visits/max*100)}%"></i></div></div><strong>${x.visits}</strong></div>`).join():'<p class="muted">No visits yet. Generate sample traffic.</p>';
$("daily").innerHTML=s.daily.length?s.daily.map(x=>`<div class="daily-row"><span>${safe(x.day)}</span><strong>${x.visits} visits</strong></div>`).join():'<p class="muted">No daily data yet.</p>';
$("events").innerHTML=e.items.length?e.items.map(x=>`<tr><td>${safe(x.ip_address)}</td><td>${safe(x.country)}</td><td>${safe(x.request_path)}</td><td>${safe(x.created_at)} UTC</td><td><span class="pill">${x.is_simulated?"SIMULATED":"RECORDED"}</span></td></tr>`).join():'<tr><td colspan="5">No events yet.</td></tr>';
notice("Connected. Analytics loaded from SQLite.");}catch(err){notice(err.message,true)}}
$("save-token").addEventListener("click",()=>{token=$("token").value.trim();sessionStorage.setItem("formaAdminToken",token);refresh()});
$("refresh").addEventListener("click",refresh);
$("simulate").addEventListener("click",async()=>{try{const count=Number($("sim-count").value);await api("/api/admin/analytics/simulate",{method:"POST",body:JSON.stringify({count})});notice(`${count} simulated visits inserted.`);await refresh()}catch(e){notice(e.message,true)}});
if(token)refresh();