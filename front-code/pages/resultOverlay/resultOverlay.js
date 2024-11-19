Page({
  data: {
    discipleName: '', // 门生名字
    selectedTopic: '', // 用户选择的主题
    systemQuestion: '', // 系统的问题
    discipleAnswer: '', // 门生的回答
    userAnswer: '', // 用户的回答
    answerTranslation: '', // 最相似回答的中文翻译
    // 用于传递给下一个页面的参数
    pic2PartReserve: '',
    pic2PartRewrite: '',
    pic2UserIdiom: '',
  },

  onLoad() {
    // 从本地存储中获取数据
    const data = wx.getStorageSync('resultData');
    if (data) {
      this.setData({
        discipleName: data.discipleName,
        selectedTopic: data.selectedTopic,
        systemQuestion: data.systemQuestion,
        discipleAnswer: data.discipleAnswer,
        userAnswer: data.userAnswer,
        answerTranslation: data.answerTranslation,
        pic2PartReserve: data.pic2PartReserve,
        pic2PartRewrite: data.pic2PartRewrite,
        pic2UserIdiom: data.pic2UserIdiom,
      });
      // 清除本地存储，避免下次进入页面时数据混淆
      wx.removeStorageSync('resultData');
    } else {
      wx.showToast({ title: '未找到结算数据', icon: 'none' });
      console.error('未找到结算数据');
    }
  },

  // 跳转到第二个结算页面
  viewMoreLunyu() {
    // 将后三个参数保存到本地存储
    wx.setStorageSync('nameResultData', {
      pic2PartReserve: this.data.pic2PartReserve,
      pic2PartRewrite: this.data.pic2PartRewrite,
      pic2UserIdiom: this.data.pic2UserIdiom,
    });
console.log(this.data.pic2PartReserve);
    wx.navigateTo({
      url: '/pages/inputName/inputName',
    });
  },

  // 保存图片功能（待实现）
  saveImage() {
    wx.showToast({ title: '保存图片功能待开发', icon: 'none' });
  },

  // 分享页面功能（待实现）
  sharePage() {
    wx.showToast({ title: '分享功能待开发', icon: 'none' });
  },
});
