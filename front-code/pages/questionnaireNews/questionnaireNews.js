const { port } = require('../config');
Page({
  data: {
    selectedTopic: '',     // 选择的话题
    dialogues: [],         // 对话内容
    inputAnswer: '',       // 用户输入
    isSubmitting: false,   // 提交按钮状态
    title: '',             // 从 options 传入的标题
    snippet: '',           // 从 options 传入的摘要
    focus: false           // 输入框的焦点状态
  },

  onLoad(options) {
    // 从上一个页面获取主题、标题和摘要
    if (options.topic && options.snippet && options.title) {
      this.setData({
        selectedTopic: decodeURIComponent(options.topic),
        title: decodeURIComponent(options.title),
        snippet: decodeURIComponent(options.snippet)
      });

      // 初始化对话内容，显示摘要和提问
      this.setData({
        dialogues: [{
          type: 'system',
          text: {
            original: this.data.snippet,
            translation: '你对该事件有什么看法?'
          }
        }]
      });
    } else {
      console.error("未传递主题、标题或摘要参数");
      wx.showToast({ title: '未获取到必要的数据', icon: 'none' });
    }
  },

  // 输入框内容变化
  onInputChange(e) {
    this.setData({
      inputAnswer: e.detail.value.trim()
    });
  },

  // 提交答案
  submitAnswer() {
    if (!this.data.inputAnswer) {
      wx.showToast({ title: '输入内容不能为空', icon: 'none' });
      return;
    }

    // 禁用提交按钮
    this.setData({
      isSubmitting: true
    });

    // 将用户的输入添加到对话框
    this.setData({
      dialogues: this.data.dialogues.concat([{
        type: 'user',
        text: this.data.inputAnswer
      }])
    });

    wx.showLoading({ title: '加载中...' });

    // 发起匹配请求
    wx.request({
      url: `${port}/online_generate/`, // 替换为实际后端地址
      method: 'POST',
      timeout: 120000,
      data: {
        topic: this.data.selectedTopic,
        role: '',
        title: this.data.title,
        question: this.data.snippet,
        dialog: this.data.inputAnswer,
        mode: 'news'
      },
      success: (res) => {
        if (res.data && res.data.answer && res.data.role) {
          const {
            answer,
            answer_translation,
            role,
            pic2_part_reserve,
            pic2_part_rewrite,
            pic2_user_idiom
          } = res.data;

          const question = this.data.dialogues[0].text.original; // 获取最初的问题

          console.log("成功接收 online_generate 接口参数");

          // 将数据保存到本地存储
          wx.setStorageSync('resultData', {
            discipleName: role,
            selectedTopic: this.data.selectedTopic,
            systemQuestion: question,
            discipleAnswer: answer,
            userAnswer: this.data.inputAnswer,
            answerTranslation: answer_translation,
            pic2PartReserve: pic2_part_reserve,
            pic2PartRewrite: pic2_part_rewrite,
            pic2UserIdiom: pic2_user_idiom,
          });

          // 跳转到结算页面
          wx.navigateTo({
            url: '/pages/resultOverlay/resultOverlay',
          });
        } else {
          wx.showToast({ title: '后端未返回有效结果', icon: 'none' });
          console.error('后端返回的数据不完整：', res.data);
        }
      },
      fail: (err) => {
        console.error("请求失败：", err);
        wx.showToast({ title: '提交失败，请检查网络', icon: 'none' });
      },
      complete: () => {
        // 请求完成后重新启用提交按钮
        this.setData({
          isSubmitting: false,
          inputAnswer: '', // 清空输入框
          focus: true      // 聚焦到输入框
        });
        wx.hideLoading();
      }
    });
  }
});
