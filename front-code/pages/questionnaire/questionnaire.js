Page({
  data: {
    selectedTopics: [],  // 选中的话题
    currentQuestion: {  // 当前问题的原文和翻译
      original: '子曰：“学而时习之，不亦说乎？”',
      translation: '孔子说：“学习并时常复习，不是很愉快吗？”'
    },
    inputAnswer: '',  // 用户输入的答案
    dialogues: [  // 对话记录
      { type: 'system', text: { original: '子曰：“学而时习之，不亦说乎？”', translation: '孔子说：“学习并时常复习，不是很愉快吗？”' } }
    ],
    focus: false,
    progress: 0,  // 进度条进度
    totalQuestions: 5,  // 总问题数量，后期可以从后端获取
    answeredQuestions: 0  // 已回答的问题数量
  },

  onLoad(options) {
    const topics = JSON.parse(decodeURIComponent(options.topics));
    this.setData({
      selectedTopics: topics
    });

    console.log('接收到的话题:', this.data.selectedTopics);
  },

  // 获取用户输入
  onInputChange(e) {
    this.setData({
      inputAnswer: e.detail.value
    });
  },

  // 提交答案
  submitAnswer() {
    const { inputAnswer, dialogues, answeredQuestions, totalQuestions } = this.data;
    
    if (!inputAnswer.trim()) {
      wx.showToast({
        title: '请输入答案',
        icon: 'none'
      });
      return;
    }

    // 显示用户输入的答案
    this.setData({
      dialogues: [...dialogues, { type: 'user', text: inputAnswer }],
      inputAnswer: '',  // 清空输入框
      answeredQuestions: answeredQuestions + 1  // 更新已回答问题数
    });

    // 更新进度条
    const progress = ((answeredQuestions + 1) / totalQuestions) * 100;
    this.setData({
      progress: progress
    });

    // 检查是否完成所有问题
    if (progress >= 100) {
      // 模拟跳转到结算页面
      wx.navigateTo({
        url: '/pages/resultOverlay/resultOverlay'
      });
      return;
    }

    // 模拟系统回复（注释掉的后端请求部分）
    /*
    wx.request({
      url: 'https://your-backend-api.com/submit-answer', // 替换成后端的接口
      method: 'POST',
      data: {
        topics: this.data.selectedTopics,
        answer: inputAnswer
      },
      success: (res) => {
        const systemReply = res.data.reply;
        this.setData({
          dialogues: [...this.data.dialogues, { type: 'system', text: systemReply }]
        });
      },
      fail: () => {
        wx.showToast({
          title: '请求失败，请稍后再试',
          icon: 'none'
        });
      }
    });
    */

    // 示例系统回复
    const exampleReply = { original: '曾子曰：“吾日三省吾身。”', translation: '曾子说：“我每天反省自己三次。”' };
    this.setData({
      dialogues: [...this.data.dialogues, { type: 'system', text: exampleReply }]
    });
  }
});