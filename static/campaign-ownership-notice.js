(() => {
    'use strict';
    function install(){
        const notice=document.getElementById('campaignOwnershipNotice');
        const info=document.getElementById('activeCampaignInfo');
        if(!notice)return;
        let generation=0;
        async function draw(){
            const current=++generation;
            try{
                const response=await fetch('/api/campaigns',{cache:'no-store'});
                if(!response.ok)return;
                const data=await response.json();if(current!==generation)return;
                const count=data.campaigns?.length||0;
                notice.hidden=Boolean(data.active);
                notice.textContent=count?'Select a campaign you own and click Switch.':'No campaigns are assigned to your admin account. Ask a superadmin to assign a campaign, or create a new campaign.';
            }catch{ /* Normal page/session error handling remains authoritative. */ }
        }
        if(info)new MutationObserver(draw).observe(info,{childList:true,subtree:true,characterData:true});
        draw();
    }
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
})();
