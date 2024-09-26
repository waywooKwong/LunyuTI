Page({
  data: {
    topics: [
      { name: '仁', selected: false },
      { name: '义', selected: false },
      { name: '礼', selected: false },
      { name: '智', selected: false },
      { name: '信', selected: false },
      { name: '孝', selected: false },
      { name: '忠', selected: false },
      { name: '勇', selected: false },
      { name: '和', selected: false },
      { name: '德', selected: false }
    ],
    selectedCount: 0
  },
  toggleTopic(e) {
    const index = e.currentTarget.dataset.index
    let { topics, selectedCount } = this.data
    
    if (topics[index].selected && selectedCount > 0) {
      selectedCount--
    } else if (!topics[index].selected && selectedCount < 3) {
      selectedCount++
    } else {
      return
    }

    topics[index].selected = !topics[index].selected
    
    this.setData({ topics, selectedCount })
  },
  confirmSelection() {
    const selectedTopics = this.data.topics
      .filter(topic => topic.selected)
      .map(topic => topic.name)
    
    console.log('选中的话题:', selectedTopics)
     //TODO: 跳转到下一个页面,并传递选中的话题
     wx.navigateTo({
       url: `/pages/questionnaire/questionnaire?topics=${JSON.stringify(selectedTopics)}`
     })
  }
})