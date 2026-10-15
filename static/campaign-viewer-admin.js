(() => {
    'use strict';
    function install(){
        const panel=document.getElementById('campaignViewerAccess');if(!panel)return;
        const heading=document.getElementById('campaignViewerAccessTitle');
        const list=document.getElementById('campaignViewerUsers');
        const notice=document.getElementById('campaignViewerNotice');
        const save=document.getElementById('saveCampaignViewers');
        let campaign=null,generation=0,saving=false;
        async function api(url,options){
            const response=await fetch(url,{cache:'no-store',...options});
            if(!response.ok){const body=await response.json().catch(()=>({}));throw new Error(typeof body.detail==='string'?body.detail:`Request failed (${response.status})`);}
            return response.json();
        }
        function draw(data){
            campaign=data.campaign;heading.textContent='Viewer access: '+campaign.name;list.replaceChildren();
            for(const user of data.users){
                const label=document.createElement('label'),check=document.createElement('input');
                check.type='checkbox';check.value=user.id;check.checked=user.granted;
                label.append(check,document.createTextNode(' '+user.username));label.style.display='block';list.append(label);
            }
            if(!data.users.length)list.textContent='No client-role users exist. A superadmin can create them on the Users page.';
        }
        async function refresh(force=false){
            const request=++generation;
            try{
                const campaigns=await api('/api/campaigns');if(request!==generation)return;
                if(!force&&String(campaigns.active)===campaign?.id)return;
                save.disabled=true;campaign=null;list.replaceChildren();notice.textContent='Loading viewer access…';
                if(campaigns.active==null){notice.textContent='Select an active campaign first.';return;}
                const data=await api(`/api/campaigns/${encodeURIComponent(campaigns.active)}/viewers`);
                if(request!==generation)return;draw(data);notice.textContent='';save.disabled=saving;
            }catch(error){if(request===generation)notice.textContent=error.message;}
        }
        save.onclick=async()=>{
            if(!campaign||saving)return;
            const target=campaign.id,ids=[...list.querySelectorAll('input:checked')].map(input=>input.value);
            saving=true;save.disabled=true;notice.textContent='Saving viewer access…';
            try{
                await api(`/api/campaigns/${encodeURIComponent(target)}/viewers`,{
                    method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_ids:ids}),
                });
                if(campaign?.id===target)notice.textContent='Viewer access saved.';
            }catch(error){if(campaign?.id===target)notice.textContent=error.message;}
            finally{saving=false;save.disabled=!campaign;}
        };
        const info=document.getElementById('activeCampaignInfo');
        if(info)new MutationObserver(()=>refresh()).observe(info,{childList:true,subtree:true,characterData:true});
        panel.addEventListener('toggle',()=>{if(panel.open)refresh(true);});refresh();
    }
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
})();
