Page({
  data: {
    discipleName: '', // 门生名字
    selectedTopic: '', // 用户选择的主题
    systemQuestion: '', // 系统的问题
    discipleAnswer: '', // 门生的回答
    userAnswer: '', // 用户的回答
    answerTranslation: '', // 最相似回答的中文翻译
  },

  onLoad() {
    // 从本地存储中获取数据
    const data = wx.getStorageSync('resultData');
    if (data) {
      this.setData(data);
      // 清除本地存储，避免下次进入页面时数据混淆
      wx.removeStorageSync('resultData');
    } else {
      wx.showToast({ title: '未找到结算数据', icon: 'none' });
    }
  },

  saveImage() {
    wx.showToast({ title: '保存图片功能待开发', icon: 'none' });
  },

  sharePage() {
    wx.showToast({ title: '分享功能待开发', icon: 'none' });
  },

  viewMoreLunyu() {
    wx.navigateTo({
      url: '/pages/moreLunyu/moreLunyu',
    });
  },
});
