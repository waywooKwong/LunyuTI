Page({
  data: {
    dialogues: [], // 对话记录
    inputText: '', // 输入框内容
    inputPlaceholder: '请输入您的问题', // 输入框提示文字
    buttonText: '提交', // 按钮文字
    isSubmitting: false, // 提交按钮状态
    question: '', // 用户输入的问题
    dialog: '', // 用户输入的答案
    topic: '', // 从前一个页面传递的主题
    isQuestionPhase: true, // 当前是否处于问题输入阶段
    role: '', // 最相似的人物
    discipleAnswer: '', // 门生的回答
    answerTranslation: '', // 最相似回答的中文翻译
    systemQuestion: '', // 系统的问题
    showJumpButton: false, // 是否显示跳转按钮
  },

  // 接收参数（例如从前一个页面传递 topic）
  onLoad(options) {
    if (options.topic) {
      this.setData({
        topic: decodeURIComponent(options.topic), // 接收并解码主题
      });
    }
  },

  // 输入框内容变化
  onInputChange(e) {
    this.setData({
      inputText: e.detail.value.trim(),
    });
  },

  // 提交按钮点击逻辑
  onSubmit() {
    if (!this.data.inputText) {
      wx.showToast({ title: '输入内容不能为空', icon: 'none' });
      return;
    }

    if (this.data.isQuestionPhase) {
      // 保存问题并切换到答案输入阶段
      this.setData({
        question: this.data.inputText, // 保存问题
        dialogues: [
          ...this.data.dialogues,
          { id: Date.now(), type: 'user', text: this.data.inputText },
        ],
        inputText: '', // 清空输入框
        inputPlaceholder: '请输入您的答案', // 更改提示文字
        buttonText: '提交回答', // 更改按钮文字
        isQuestionPhase: false, // 切换到答案输入阶段
      });
    } else {
      // 提交问题和答案到后端
      this.setData({
        dialog: this.data.inputText, // 保存答案
        dialogues: [
          ...this.data.dialogues,
          { id: Date.now(), type: 'user', text: this.data.inputText },
        ],
      });
      this.submitToBackend(); // 提交到后端
    }
  },

  // 提交到后端
  submitToBackend() {
    this.setData({ isSubmitting: true });
    wx.showLoading({ title: '加载中...' });

    wx.request({
      url: 'http://localhost:8000/online_generate/', // 替换为实际后端地址
      method: 'POST',
      timeout: 120000,
      header: {
        'Content-Type': 'application/json',
      },
      data: {
        topic: this.data.topic,
        role: "",
        title: "",
        question: this.data.question,
        dialog: this.data.dialog,
        mode: 'custom',
      },
      success: (res) => {
        if (res.data && res.data.answer && res.data.role) {
          // 保存必要的数据
          this.setData({
            role: res.data.role, // 门生名字
            discipleAnswer: res.data.answer, // 门生的回答
            answerTranslation: res.data.answer_translation || '', // 最相似回答的中文翻译
            systemQuestion: this.data.question, // 系统的问题（即用户输入的问题）
            dialogues: [
              ...this.data.dialogues,
              {
                id: Date.now(),
                type: 'system',
                text: {
                  original: res.data.answer,
                  translation: res.data.answer_translation || '',
                },
              },
            ],
            showJumpButton: true, // 显示跳转按钮
          });
        } else {
          wx.showToast({ title: '后端未返回有效结果', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.showToast({ title: '提交失败，请检查网络', icon: 'none' });
        console.error('提交失败：', err);
      },
      complete: () => {
        wx.hideLoading();
        this.setData({ isSubmitting: false });
      },
    });
  },

  // 跳转到结算界面
  onNavigateToSettlement() {
    if (!this.data.role) {
      wx.showToast({ title: '未获取到最相似的人物', icon: 'none' });
      return;
    }

    // 使用本地存储传递数据
    wx.setStorageSync('resultData', {
      discipleName: this.data.role,
      selectedTopic: this.data.topic,
      systemQuestion: this.data.systemQuestion,
      discipleAnswer: this.data.discipleAnswer,
      userAnswer: this.data.dialog,
      answerTranslation: this.data.answerTranslation,
    });

    wx.navigateTo({
      url: '/pages/resultOverlay/resultOverlay',
    });
  },
});
