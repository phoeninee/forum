<template>
  <div class="topic-index flex">
    <div class="topics">
      <transition-group name="fade-slide-u" mode="out-in">
        <topic-intro-card
          v-for="(t, index) in topics"
          :key="index"
          :topic="t"
        />
      </transition-group>
    </div>
    <div class="aside gutter--8px">
      <el-card class="user-card" :body-style="{ padding: '0' }">
        <div class="user-avatar">
          <img :src="currentUser.avatar">
        </div>
        <el-row class="user-info">
          <el-col :span="8" class="flex flex-column tc">
            <span class="user-info-header">创建</span>
            <span class="user-info-body">{{ currentUser.topicCount }}</span>
          </el-col>
          <el-col :span="8" class="flex flex-column tc">
            <span class="user-info-header">参与</span>
            <span class="user-info-body">{{ currentUser.involvedCount }}</span>
          </el-col>
          <el-col :span="8" class="flex flex-column tc">
            <span class="user-info-header">关注者</span>
            <span class="user-info-body">{{ currentUser.follower_count }}</span>
          </el-col>
        </el-row>
      </el-card>
      <el-card class="">
        <div slot="header">话题分类</div>
        <div
          v-for="b in boards"
          :key="b.id"
          class="board"
        >
          <div class="flex justify-sb">
            <span class="name">{{ b.name }}</span>
            <span class="count">{{ b.topic_count }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import { mapState } from 'vuex'
import { Card, Row, Col } from 'element-ui'
import TopicIntroCard from '@/components/card/topic/intro'
import { copyProps, normalizeTimestamp, addBaseUrl, log, isOk } from '../../utils'
import { baseUrl } from '@/config'

Vue.use(Card)
Vue.use(Row)
Vue.use(Col)

export default {
  name: 'TopicIndex',

  components: {
    TopicIntroCard,
  },

  data() {
    return {
      topics: [],
      boards: [],
    }
  },

  computed: mapState([
    'currentUser',
  ]),

  methods: {
    getBoards() {
      let url = this.$apiRoutes.getBoards
      this.$http.get(url).then((res) => {
        if (isOk(res.status)) {
          this.boards = res.data
        }
      })
    },

    getData() {
      this.$http.get(this.$apiRoutes.getTopics).then((res) => {
        let data = res.data.map((item) => {
          // 提取话题数据，通过复制处理
          let t = copyProps(item, [
            'id',
            'content',
            'title',
            'views',
            'board_id',
            { from: 'board_name', to: 'boardName' },
            { from: 'reply_count', to: 'replyCount' },
            { from: 'user', to: 'user', handler: addBaseUrl(baseUrl, ['avatar']) },
            { from: 'created_time', to: 'createdTime', handler: normalizeTimestamp },
            { from: 'updated_time', to: 'updatedTime', handler: normalizeTimestamp },
          ])
          return t
        })
        log('topics:', data)

        this.topics = data
      })
    },
  },

  mounted() {
    this.getBoards()
    this.getData()
  },
}
</script>

<style lang="scss">
.topic-index {
  .board {
    color: $color-first;
    font-size: .9rem;

    & + .board {
      margin-top: 1rem;
    }

    .count {
      display: block;
      background-color: $color-gray1;
      text-align: center;
      width: 1.5rem;
      height: 1.5rem;
      line-height: 1.5rem;
    }
  }
}

.aside {
  width: 250px;
  flex: 0 0 250px;

  & > * {
    * + & {
      margin-bottom: .5rem;
    }
  }

  .user-card {
    .user-avatar {
      display: flex;
      margin: 2rem 0;
      img {
        border-radius: 1rem;
        height: 5rem;
        margin: auto;
      }
    }

    .user-info {
      background-color: $color-light;
      padding: .75rem;

      & > * {
        cursor: pointer;
      }

      .user-info-header {
        color: $color-gray6;
        font-size: 14px;
      }
    }
  }
}
</style>
