"use strict";
let editing = null;
let current = null;
const byId = id => document.getElementById(id);
const message = text => { byId("userMessage").textContent = text; };
async function api(path, method = "GET", body) {
  const response = await fetch(path, {method, headers: body ? {"Content-Type": "application/json"} : {}, body: body ? JSON.stringify(body) : undefined});
  if (response.status === 401) { location.assign("/login"); throw new Error("Sign in required"); }
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Invalid user data");
  return data;
}
function reset() {
  editing = null;
  byId("userForm").reset();
  byId("password").required = true;
  byId("formTitle").textContent = "Create user";
}
async function load() {
  const rows = await api("/api/users");
  byId("userRows").replaceChildren();
  for (const user of rows) {
    const row = document.createElement("tr");
    for (const value of [user.username, user.role]) {
      const cell = document.createElement("td"); cell.textContent = value; row.append(cell);
    }
    const actions = document.createElement("td");
    const edit = document.createElement("button"); edit.textContent = "Edit"; edit.type = "button";
    edit.onclick = () => {
      editing = user.id; byId("username").value = user.username; byId("role").value = user.role;
      byId("password").value = ""; byId("password").required = false;
      byId("formTitle").textContent = "Edit " + user.username; byId("username").focus();
    };
    const remove = document.createElement("button"); remove.textContent = "Delete"; remove.type = "button";
    remove.onclick = async () => {
      if (!confirm("Delete user " + user.username + "?")) return;
      try {
        await api("/api/users/" + user.id, "DELETE");
        if (user.username === current.username) { location.assign("/login"); return; }
        reset(); await load(); message("User deleted.");
      } catch (error) { message(error.message); }
    };
    actions.append(edit, remove); row.append(actions); byId("userRows").append(row);
  }
}
byId("cancelEdit").onclick = reset;
byId("userForm").onsubmit = async event => {
  event.preventDefault();
  const body = {username: byId("username").value, role: byId("role").value};
  if (byId("password").value || editing === null) body.password = byId("password").value;
  try {
    const users = editing !== null ? await api("/api/users") : [];
    const self = users.some(user => user.id === editing && user.username === current.username);
    await api(editing === null ? "/api/users" : "/api/users/" + editing, editing === null ? "POST" : "PATCH", body);
    if (self) { location.assign("/login"); return; }
    reset(); await load(); message("User saved.");
  } catch (error) { message(error.message); }
};
(async () => { try { current = await api("/api/me"); await load(); } catch (error) { message(error.message); } })();
