export default class HttpService {
  signIn(signInValues) {
    return fetch("/user/login", {
      method: "POST",
      body: signInValues,
      headers: getAuthHeader(),
    }).then((res) => {
      if (res.status === 401) {
        relogin();
      }
      return res.json();
    });
  }

  upload(uploadFormdata) {
    return fetch("/upload", {
      method: "POST",
      body: uploadFormdata,
      headers: getAuthHeader(),
    }).then((res) => {
      if (res.status === 401) {
        relogin();
      }
      return res.json();
    });
  }

  getAll() {
    return fetch("/query_all", { headers: getAuthHeader() }).then((res) => {
      if (res.status === 401) {
        relogin();
      }
      return res.json();
    });
  }

  delete(id) {
    return fetch(`/delete/${id}`, {
      method: "DELETE",
      headers: getAuthHeader(),
    }).then((res) => {
      if (res.status === 401) {
        relogin();
      }
      return res.json();
    });
  }

  getLabel() {
    return fetch("/current_label").then((res) => {
      if (res.status === 401) {
        relogin();
      }
      return res.json();
    });
  }
}

function getAuthHeader() {
  const userProfile = localStorage.getItem("userProfile");
  if (!userProfile) {
    return {};
  }
  const { access_token: token } = JSON.parse(userProfile);
  return { Authorization: token };
}

function relogin() {
  localStorage.removeItem("userProfile");
  localStorage.removeItem("isAuthenticated");
  window.location.replace("signin.html");
}
