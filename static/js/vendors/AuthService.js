export default class AuthService {
  isAuthenticated = false;

  /**
   * @param {*} httpService 请求服务, 发起登录请求
   * @param {Storage} storageService 存储服务, 用于本地存储用户信息
   */
  constructor(httpService, storageService, notificationService) {
    this.httpService = httpService;
    this.storageService = storageService;
    this.notificationService = notificationService;
    this.init();
  }

  init() {
    this.isAuthenticated =
      this.storageService.getItem("isAuthenticated") || false;
  }

  validateSignedIn(userProfile) {
    return userProfile.code === 200 && userProfile.data.access_token;
  }

  /**
   * 登录
   * @returns {Promise<void>} 无返回值
   * @throws {Error} 登录失败时抛出异常
   * @example
   */
  signIn(signInValues = {}) {
    this.isAuthenticated = false;
    return this.httpService
      .signIn(signInValues)
      .then((userProfile = {}) => {
        const valid = this.validateSignedIn(userProfile);
        if (!valid) {
          return Promise.reject(new Error("登录失败" + userProfile.message));
        }

        this.isAuthenticated = true;
        this.storageService.setItem("isAuthenticated", true);
        this.storageService.setItem(
          "userProfile",
          JSON.stringify(userProfile.data)
        );
        this.notificationService.notify("登录成功" + userProfile.message);
        return userProfile;
      })
      .catch((error) => {
        this.notificationService.notify(error.message || "登录失败");
        throw error;
      });
  }

  /**
   * 退出登录
   * @returns {void} 无返回值
   */
  signOut() {
    this.storageService.removeItem("isAuthenticated");
    this.storageService.removeItem("userProfile");
    this.isAuthenticated = false;
  }

  /**
   * @returns {boolean} 是否已登录
   */
  get isAuthenticated() {
    return this.isAuthenticated;
  }

  getUserProfile() {
    return JSON.parse(this.storageService.getItem("userProfile"));
  }
}
