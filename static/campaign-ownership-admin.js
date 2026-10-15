/* Superadmin ownership management on the existing Users page. */
(() => {
    'use strict';
    const rows=document.getElementById('campaignOwnerRows');
    const notice=document.getElementById('campaignOwnerNotice');
    const refreshButton=document.getElementById('refreshCampaignOwners');
    if(!rows||!notice||!refreshButton)return;
    let loading=false;
    async function api(url, options={}){
        const response=await fetch(url,{cache:'no-store',...options});
        const body=await response.json().catch(()=>({}));
        if(!response.ok)throw new Error(typeof body.detail==='string'?body.detail:`Request failed (${response.status})`);
        return body;
    }
    async function refresh(){
        if(loading)return;loading=true;refreshButton.disabled=true;notice.textContent='Loading campaign owners…';
        try{
            const data=await api('/api/campaign-ownership');rows.replaceChildren();
            for(const campaign of data.campaigns){
                const row=document.createElement('tr'),name=document.createElement('td'),owner=document.createElement('td'),actions=document.createElement('td');
                name.textContent=campaign.name;
                const select=document.createElement('select');select.setAttribute('aria-label','Owner for '+campaign.name);
                const empty=document.createElement('option');empty.value='';empty.textContent='Unassigned';select.append(empty);
                for(const admin of data.admins){const option=document.createElement('option');option.value=admin.id;option.textContent=admin.username;select.append(option);}
                select.value=campaign.owner_user_id||'';owner.append(select);
                const button=document.createElement('button');button.type='button';button.textContent='Save owner';
                button.onclick=async()=>{
                    const id=select.value;
                    if(!confirm(`Assign ${campaign.name} to ${id?select.selectedOptions[0].textContent:'Unassigned'}?`))return;
                    button.disabled=true;select.disabled=true;
                    try{
                        await api('/api/campaign-ownership/'+encodeURIComponent(campaign.id),{
                            method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({owner_user_id:id||null}),
                        });
                        notice.textContent='Campaign owner saved.';
                    }catch(error){notice.textContent=error.message;}
                    finally{button.disabled=false;select.disabled=false;}
                };
                actions.append(button);row.append(name,owner,actions);rows.append(row);
            }
            notice.textContent=data.campaigns.length?'':'No campaigns exist.';
        }catch(error){notice.textContent=error.message;}
        finally{loading=false;refreshButton.disabled=false;}
    }
    refreshButton.onclick=refresh;
    const users=document.getElementById('userRows');
    if(users)new MutationObserver(refresh).observe(users,{childList:true});
    refresh();
})();
