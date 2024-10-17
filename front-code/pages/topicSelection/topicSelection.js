Page({
  data: {
    topics: [],  // 主题列表
    selectedTopic: null,  // 选中的主题
  },
  
  onLoad() {
    // 初始化主题列表
    this.setData({
      topics: [
        { name: "执政之道", selected: false },
        { name: '道德修养', selected: false },
        { name: '美与艺术', selected: false },
        { name: '孝道的理解', selected: false },
        { name: '道德与礼仪', selected: false },
        { name: '学习与志向', selected: false },
        { name: '君子的修养', selected: false },
        { name: '仁爱与智慧', selected: false },
        { name: '对友谊的看法', selected: false },
        { name: '社会和谐', selected: false },
        { name: '对生死的看法', selected: false },
        { name: '以德治国', selected: false },
        { name: '贤者的品质', selected: false },
        { name: '教育与教导', selected: false },


        // 添加更多主题
      ]
    });
  },

  toggleTopic(e) {
    const index = e.currentTarget.dataset.index;
    
    // 将所有主题的 selected 状态设为 false
    this.data.topics.forEach((topic, i) => {
      topic.selected = (i === index);
    });
  
    this.setData({
      selectedTopic: this.data.topics[index].selected ? this.data.topics[index].name : null,
      topics: this.data.topics,
    });
  }
  ,

  confirmSelection() {
    // 确认选择后，获取问题
    wx.request({
      url: 'http://localhost:8000/get_question/',
      method: 'GET',
      data: { theme_from_front: this.data.selectedTopic },
      success: (res) => {
        console.log(res.data.question)
        if (res.data) {
          // 跳转到问答页面，传递问题和翻译
          wx.navigateTo({
            url: `/pages/questionnaire/questionnaire?theme=${encodeURIComponent(this.data.selectedTopic)}&question=${encodeURIComponent(res.data.question)}&translation=${encodeURIComponent(res.data.question_translation)}`,
          });
        }
      },
      fail: (err) => {
        console.error(err);
      }
    });
  }
});
