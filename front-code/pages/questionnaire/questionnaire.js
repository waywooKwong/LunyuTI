const { port } = require('../config');
Page({
  data: {
    selectedTopic: '',
    dialogues: [], // 对话内容
    inputAnswer: '', // 用户输入
    progress: 0,
    isSubmitting: false, // 提交按钮状态
    question: '', // 获取的题目
    questionTranslation: '', // 题目的翻译
  },

  onLoad(options) {
    // 从选主题页面获取主题
    if (options.theme) {
      this.setData({
        selectedTopic: decodeURIComponent(options.theme)
      });

      // 初始化对话内容
      this.getQuestion();
    } else {
      console.error("未传递主题参数");
    }
  },

  getQuestion() {
    wx.request({
      url: `${port}/get_question/`,
      method: 'GET',
      data: {
        theme_from_front: this.data.selectedTopic
      },
      success: (res) => {
        if (res.data) {
          this.setData({
            question: res.data.question,
            questionTranslation: res.data.question_translation,
            dialogues: [{
              type: 'system',
              text: {
                original: res.data.question,
                translation: res.data.question_translation
              }
            }]
          });
        } else {
          wx.showToast({ title: '未获取到题目', icon: 'none' });
        }
      },
      fail: (err) => {
        console.error(err);
        wx.showToast({ title: '获取题目失败', icon: 'none' });
      }
    });
  },

  onInputChange(e) {
    this.setData({
      inputAnswer: e.detail.value
    });
  },

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
      url: `${port}/get_answer/`,
      method: 'GET',
      data: {
        question_from_back: this.data.question,
        answer_from_front: this.data.inputAnswer,
        request_topic: this.data.selectedTopic, // 新增参数
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

          // 将数据保存到本地存储
          wx.setStorageSync('resultData', {
            discipleName: role,
            selectedTopic: this.data.selectedTopic,
            systemQuestion: this.data.question,
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
        console.error(err);
        wx.showToast({ title: '请求失败，请检查网络', icon: 'none' });
      },
      complete: () => {
        // 请求完成后重新启用提交按钮
        this.setData({
          isSubmitting: false,
          inputAnswer: '' // 清空输入框
        });
        wx.hideLoading();
      }
    });
  }
});
