import { auth, notification } from "./init.js";

const rules = {
  username: [
    {
      required: true,
      message: "Username is required",
      min: 3,
      max: 20,
    },
  ],
  password: [
    {
      required: true,
      min: 6,
      max: 20,
      message: "Password is required",
    }
  ],
};

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("signInForm");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formValues = getFormValues(form);
    const isValid = validate(formValues, rules);
    if (!isValid) {
      notification.error("账号或密码的格式不正确");
      return;
    }

    const loginFormdata = new FormData();
    loginFormdata.append("username", formValues.username);
    loginFormdata.append("password", formValues.password);

    auth.signIn(loginFormdata).then(() => {
      window.location.replace("/index.html");
    });
  });
});

function getFormValues(form) {
  const formData = new FormData(form);
  return Object.fromEntries(formData);
}

/**
 * 表单验证
 * @param {Object} values 表单值
 * @param {Object} rules 验证规则
 * @returns {Boolean} 是否验证通过
 */
function validate(values = {}, rules = {}) {
  for (const key in rules) {
    const value = values[key];
    const rule = rules[key];

    for (const item of rule) {
      if (item.required && !value) {
        // notification.error(item.message);
        return false;
      }

      if (item.min && value.length < item.min) {
        // notification.error(item.message);
        return false;
      }

      if (item.max && value.length > item.max) {
        // notification.error(item.message);
        return false;
      }
    }
  }

  return true;
}
