Page({
  data: {
    selectedTopic: '',
    dialogues: [], // 对话内容
    inputAnswer: '', // 用户输入
    progress: 0,
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
      url: 'http://localhost:8000/get_question/',
      method: 'GET',
      data: {
        theme_from_front: this.data.selectedTopic
      },
      success: (res) => {
        if (res.data) {
          this.setData({
            dialogues: [{
              type: 'system',
              text: {
                original: res.data.question,
                translation: res.data.question_translation
              }
            }]
          });
        }
      },
      fail: (err) => {
        console.error(err);
      }
    });
  },

  onInputChange(e) {
    this.setData({
      inputAnswer: e.detail.value
    });
  },

  submitAnswer() {
    // 将用户的输入添加到对话框
    this.setData({
      dialogues: this.data.dialogues.concat([{
        type: 'user',
        text: this.data.inputAnswer
      }])
    });

    // 发起匹配请求
    wx.request({
      url: 'http://localhost:8000/get_answer/',
      method: 'GET',
      data: {
        theme_from_front: this.data.selectedTopic,
        answer_from_front: this.data.inputAnswer,
      },
      success: (res) => {
        if (res.data) {
          const {
            answer,
            role
          } = res.data;

          // 跳转到结算页面，并传递结果和role
          wx.navigateTo({
            url: `/pages/resultOverlay/resultOverlay?answer=${encodeURIComponent(answer)}&role=${encodeURIComponent(role)}`,
          });
        }
      },
      fail: (err) => {
        console.error(err);
      }
    });

    // 清空输入框
    this.setData({
      inputAnswer: ''
    });
  }

})