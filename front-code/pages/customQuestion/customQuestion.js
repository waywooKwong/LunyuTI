Page({
  data: {
    dialogues: [], // 对话记录
    inputText: '', // 输入框内容
    inputPlaceholder: '请输入您的问题', // 输入框提示文字
    buttonText: '提交', // 按钮文字
    isSubmitting: false, // 提交按钮状态
    question: '', // 用户输入的问题
    dialog: '', // 用户输入的答案
    topic: '君子的修养', // 示例主题，从前一个页面传递
    isQuestionPhase: true, // 当前是否处于问题输入阶段
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
        inputText: '', // 清空输入框
        inputPlaceholder: '请输入您的答案', // 更改提示文字
        buttonText: '提交回答', // 更改按钮文字
        isQuestionPhase: false, // 切换到答案输入阶段
      });
    } else {
      // 提交问题和答案到后端
      this.setData({
        dialog: this.data.inputText, // 保存答案
      });
      this.submitToBackend(); // 提交到后端
    }
  },

  // 提交到后端
  submitToBackend() {
    this.setData({ isSubmitting: true });

    wx.request({
      url: 'http://localhost:8000/online_generate/', // 替换为实际后端地址
      method: 'POST',
      header: {
        'Content-Type': 'application/json', // 确保发送 JSON 数据
      },
      data: {
        topic: this.data.topic, // 当前主题
        role: "",
        title:"",
        question: this.data.question, // 用户输入的问题
        dialog: this.data.dialog, // 用户的答案
        mode: 'custom', // 自定义模式
      },
      success: (res) => {
        if (res.data && res.data.answer && res.data.role) {
          // 显示结果或跳转到结果页面
          wx.navigateTo({
            url: `/pages/resultOverlay/resultOverlay?answer=${encodeURIComponent(res.data.answer)}&role=${encodeURIComponent(res.data.role)}`,
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
        this.setData({ isSubmitting: false });
      },
    });
  },
});
