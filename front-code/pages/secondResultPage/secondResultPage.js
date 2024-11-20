Page({
  data: {
    userName: '',             // 用户名
    pic2PartReserve: '',      // 原文不需要改动的内容（黑色）
    pic2UserIdiom: '',        // 用户的论语（红色）
    pic2PartRewrite: '',      // 原文需要重写的内容（灰色）
  },

  onLoad() {
    // 从本地存储中获取数据
    const data = wx.getStorageSync('secondResultData');
    if (data) {
      this.setData({
        pic2PartReserve: data.pic2PartReserve,
        pic2PartRewrite: data.pic2PartRewrite,
        pic2UserIdiom: data.pic2UserIdiom,
        userName: data.userName,
      });

      // 清除本地存储，避免数据残留
      wx.removeStorageSync('secondResultData');
    } else {
      wx.showToast({ title: '未找到数据', icon: 'none' });
      console.error('未找到从前一个页面传递的数据');
    }
  },
});
