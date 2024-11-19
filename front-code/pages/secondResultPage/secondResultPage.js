// pages/resultOverlay2/resultOverlay2.js
Page({
  data: {
    userName: '',             // 用户名，可以根据需要设置
    pic2PartReserve: '',    // 原文不需要改动的内容
    pic2PartRewrite: '',    // 原文需要重写的内容
    pic2UserIdiom: '',      // 用户的论语（改写后的内容）
  },

  onLoad() {
    // 从本地存储中获取数据
    const data = wx.getStorageSync('secondResultData');
    if (data) {
      this.setData({
        pic2PartReserve: data.pic2PartReserve,
        pic2PartRewrite: data.pic2PartRewrite,
        pic2UserIdiom: data.pic2UserIdiom,
        userName: data.userName 
      });
      // 清除本地存储，避免数据残留
      wx.removeStorageSync('pic2Data');
    } else {
      wx.showToast({ title: '未找到数据', icon: 'none' });
      console.error('未找到从前一个页面传递的数据');
    }
  },

  // 如果需要其他生命周期函数或方法，可以在此添加
});
