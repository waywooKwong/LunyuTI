Page({
  data: {
    discipleImageUrl: '', // 弟子头像的URL
    discipleName: '', // 弟子名字
    discipleDescription: '', // 弟子描述
    confuciusQuote: '', // 孔子的原话
    answer: '', // 相似度最高的原始答案
  },

  // 页面加载时触发
  onLoad(options) {
    // 获取传递过来的弟子名字、回答和问题
    const discipleName = decodeURIComponent(options.role);
    const confuciusQuote = decodeURIComponent(options.question); // 获取传递过来的问题
    const answer = decodeURIComponent(options.answer);
  
    // 设置页面的数据
    this.setData({
      discipleName: discipleName,
      discipleDescription: `你与${discipleName}最为相似`,
      confuciusQuote: confuciusQuote, // 孔子的原话
      answer: answer // 相似度最高的原始答案
    });

    // 根据弟子名字直接设置头像
    this.setDiscipleImage(discipleName);
  },

  // 根据弟子名字设置头像
  setDiscipleImage(discipleName) {
    const imageMap = {
      '颜渊': '/images/yanhui.png',
      '曾皙': '/images/zengzi.png',
      '子夏': '/images/zixia.png',
      '子游': '/images/ziyou.png',
      '子贡': '/images/zigong.png',
      '子禽': '/images/ziqin.png',
      '子张': '/images/zizhang.png',
      '宰我': '/images/zaiwo.png',
      '公治长': '/images/gongzhichang.png',
      '南容': '/images/nanrong.png',
      '子贱': '/images/zijian.png',
      '子路': '/images/zilu.png',
      '冉子': '/images/ranzi.png',
      '樊迟': '/images/fanchi.png',
      '仲弓': '/images/zhonggong.png',
      '司马牛': '/images/simaniu.png',
      '冉有': '/images/ranyou.png',
      '南宫适': '/images/nangongshi.png',
      // 添加其他弟子的头像路径
    };

    this.setData({
      discipleImageUrl: imageMap[discipleName] || '/images/default.png'
    });
  },

  // 保存图片
  saveImage() {
    // 保存图片的逻辑
    wx.canvasToTempFilePath({
      canvasId: 'resultCanvas', // 假设绘制结果的canvas id
      success: function (res) {
        wx.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: function () {
            wx.showToast({
              title: '图片已保存',
              icon: 'success'
            });
          },
          fail: function (err) {
            console.error("保存图片失败", err);
            wx.showToast({
              title: '保存失败',
              icon: 'none'
            });
          }
        });
      },
      fail: function (err) {
        console.error("生成图片失败", err);
      }
    });
  },

  // 分享页面功能
  sharePage() {
    wx.showShareMenu({
      withShareTicket: true,
      success: () => {
        wx.showToast({
          title: '分享成功',
          icon: 'success'
        });
      },
      fail: (err) => {
        console.error("分享失败", err);
        wx.showToast({
          title: '分享失败',
          icon: 'none'
        });
      }
    });
  }
});