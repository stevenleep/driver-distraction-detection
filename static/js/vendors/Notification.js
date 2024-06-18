export default class Notification {
  /**
   * @param {string} message 通知内容
   * @returns {void} 无返回值
   */
  notify(message) {
    alert(message);
  }

  error(message) {
    this.notify(message);
  }
}
