(() => {
    'use strict';
    const heading=document.getElementById('clientCampaign');
    const dialog=document.createElement('dialog');dialog.id='viewerCampaignDialog';
    dialog.setAttribute('aria-labelledby','viewerCampaignTitle');
    const title=document.createElement('h2');title.id='viewerCampaignTitle';title.textContent='Select campaign';
    const notice=document.createElement('p');notice.setAttribute('role','status');
    const list=document.createElement('div');list.className='viewer-campaign-list';
    const close=document.createElement('button');close.type='button';close.textContent='Cancel';
    dialog.append(title,notice,list,close);document.body.append(dialog);
    let required=false,choices=[],selected=null;
    const open=()=>{if(choices.length&&!dialog.open)dialog.showModal();};
    heading?.addEventListener('click',()=>{if(choices.length>1)open();});
    close.onclick=()=>{if(!required)dialog.close();};
    dialog.addEventListener('cancel',event=>{if(required)event.preventDefault();});
    window.renderViewerCampaignSelection=state=>{
        if(state.viewer_auth_required){location.replace('/login');return;}
        choices=state.viewer_campaigns||[];selected=state.campaign?.id||null;
        required=Boolean(state.viewer_selection_required);
        if(heading){
            heading.disabled=choices.length<2;
            heading.classList.toggle('campaign-switchable',choices.length>1);
            heading.title=choices.length>1?'Switch campaign':'';
            if(!selected)heading.textContent=choices.length?'Select campaign':'No campaign access';
        }
        notice.textContent=state.viewer_access_message||'';
        if(!choices.length&&heading)heading.textContent=notice.textContent||'No campaign access';
        const signature=JSON.stringify([choices,selected]);
        if(list.dataset.signature!==signature){
            list.dataset.signature=signature;list.replaceChildren();
            for(const campaign of choices){
                const button=document.createElement('button');button.type='button';button.textContent=campaign.name;
                button.setAttribute('aria-current',String(campaign.id===selected));
                button.onclick=()=>{
                    const url=new URL(location.href);url.pathname='/display';url.search='';
                    url.searchParams.set('campaign_id',campaign.id);location.replace(url.toString());
                };
                list.append(button);
            }
        }
        close.hidden=required;
        if(required)open();else if(!choices.length&&dialog.open)dialog.close();
    };
})();
