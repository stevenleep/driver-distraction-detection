import AuthService from "./vendors/AuthService.js";
import HttpService from "./vendors/HttpService.js";
import Notification from "./vendors/Notification.js";

const notification = new Notification();
const httpService = new HttpService();

const auth = new AuthService(httpService, localStorage, notification);

export { auth, notification, httpService };
