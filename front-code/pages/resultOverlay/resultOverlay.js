Page({
  data: {
    discipleName: '曾子',  // 示例孔子弟子名
    discipleImageUrl: '/assets/images/zengzi.png',  // 示例孔子弟子画像
    confuciusQuote: '吾日三省吾身：为人谋而不忠乎？与朋友交而不信乎？传不习乎？',
    translatedUserQuote: '吾必每日三思己行，修正以为。',
  },

  // 保存图片功能
  saveImage() {
    wx.showToast({
      title: '保存图片成功',
      icon: 'success'
    });
    // 这里可以调用 wx.canvasToTempFilePath() 实现图片保存
  },

  // 转发功能
  sharePage() {
    wx.showShareMenu({
      withShareTicket: true
    });
  }
});
