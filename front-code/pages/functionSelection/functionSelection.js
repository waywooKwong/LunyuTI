Page({
  data: {
    topic: "", // 接收传递的主题
  },

  onLoad(options) {
    this.setData({
      topic: decodeURIComponent(options.theme),
    });
  },

  onCustomQuestion() {
    // 跳转到自定义问答页面
    wx.navigateTo({
      url: `/pages/customQuestion/customQuestion?topic=${encodeURIComponent(this.data.topic)}`,
    });
  },

  onNormalQuestion() {
    // 跳转到普通问答页面
    wx.navigateTo({
      url: `/pages/questionnaire/questionnaire?theme=${encodeURIComponent(this.data.topic)}`,
    });
  },

  onNewsQuestion(){
    //跳转到新闻问答页面
    wx.navigateTo({
      url:  `/pages/new/new?topic=${encodeURIComponent(this.data.topic)}`,
    })
  }
});
