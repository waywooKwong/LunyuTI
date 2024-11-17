Page({
  data: {
    discipleName: '', // 门生名字，从后端传递
    discipleDescription: '', // 门生简介，从后端传递
    selectedTopic: '', // 用户选择的主题，从前一个页面传递
    systemQuestion: '', // 系统提供的问题，从后端传递
    discipleAnswer: '', // 门生的回答，从后端传递
    userAnswer: '' // 用户的回答，从前一个页面传递
  },

  onLoad(options) {
    this.setData({
      discipleName: decodeURIComponent(options.discipleName),
      discipleDescription: decodeURIComponent(options.discipleDescription),
      selectedTopic: decodeURIComponent(options.selectedTopic),
      systemQuestion: decodeURIComponent(options.systemQuestion),
      discipleAnswer: decodeURIComponent(options.discipleAnswer),
      userAnswer: decodeURIComponent(options.userAnswer)
    });
  },

  saveImage() {
    wx.showToast({ title: '保存图片功能待开发', icon: 'none' });
  },

  sharePage() {
    wx.showToast({ title: '分享功能待开发', icon: 'none' });
  },

  viewMoreLunyu() {
    wx.navigateTo({
      url: '/pages/moreLunyu/moreLunyu'
    });
  }
});
