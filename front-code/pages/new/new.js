Page({

  /**
   * 页面的初始数据
   */
  data: {
    topic: '',
    themeData: []
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    if (options.topic) {
      this.setData({
        topic: decodeURIComponent(options.topic), // 接收并解码主题

      });
      this.fetchThemeData(this.topic);
    }
  },

  fetchThemeData(topic) {
    wx.cloud.init({
      env: 'lunyu-yun-1gwm9lfhd499c7bf'
    });
    // 1. 获取数据库引用
    const db = wx.cloud.database({
      env: 'lunyu-yun-1gwm9lfhd499c7bf'
    });
    // 2. 构造查询语句
    db.collection('news').where({
      theme: topic
    }).get({
      success: (res) => {
        if (res.data.length > 0) {
          console.log(res.data);
          this.setData({
            themeData: res.data
          });
        }
      },
      fail: (err) => {
        console.error(err);
      }
    });
  },

  navigateToQuestionnaire(e) {
    const { topic, title, snippet } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/questionnaireNews/questionnaireNews?topic=${topic}&title=${title}&snippet=${snippet}`
    });
  },

  // 其他生命周期函数...

});