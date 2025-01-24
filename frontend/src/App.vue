<template>
    <el-config-provider :locale="locale">
        <div v-if="!screenCheck" class="small-screen">
            <div><span style="letter-spacing: 20px">iWik</span>i</div>
            <div style="font-size: 16px; text-align: center;">
                {{ $t('mobileNotice') }}
            </div>
        </div>
        <div v-loading="mainLoading" v-if="screenCheck" class="app-container">
            <transition name="el-fade-in">
                <Login v-if="showLogin" />
            </transition>
            <transition name="el-fade-in">
                <EditUserInfo v-if="showEditUser" />
            </transition>
            <transition name="el-fade-in">
                <VersionLog v-if="showVersion" />
            </transition>
            <el-header class="app-header" height="61px" v-if="!isMobile">
                <div class="el-menu-demo">
                    <div class="menu">
                        <router-link to="/" class="header-menu-home">
                            <img src="/favicon.webp" alt="logo.jpg" style="width: 32px; height: 32px; margin: 0 10px 0 0;">
                            <h2 class="header-menu-home-title">
                                iWiki
                            </h2>
                        </router-link>
                        <el-menu :default-active="activeIndex" :router="true" mode="horizontal" :ellipsis="false">
                            <el-menu-item v-for="item in menu" v-show="!item.disabled" :key="item.index" :route="item.route" :index="item.index">
                                {{ item.name }}
                            </el-menu-item>
                        </el-menu>
                    </div>
                    <div class="right-bar">
                        <el-link :underline="false" class="version" @click="showVersionTab">
                            <i class="fa-regular fa-question-circle" />
                        </el-link>
                        <el-link :underline="false" type="primary" class="locale" @click="toggleLang">
                            <i class="fa-solid fa-globe" />
                            <span>{{ curLocaleName }}</span>
                        </el-link>
                        <div class="user-login">
                            <el-link :underline="false" type="primary" v-show="!user.auth" @click="store.commit('setLogin', true)">
                                {{ $t('loginLogout') }}
                            </el-link>
                            <el-link :underline="false" class="logout-button" type="primary" v-show="user.auth" @click="showLogout">
                                <i class="fa-solid fa-user" />
                                {{ user.username }}
                            </el-link>
                        </div>
                    </div>
                </div>
            </el-header>
            <el-main>
                <router-view />
            </el-main>
        </div>
    </el-config-provider>
</template>

<script setup>
    import Login from './views/Login.vue'
    import { computed, onMounted, ref } from 'vue'
    import { useStore } from 'vuex'
    import { useRoute, useRouter } from 'vue-router'
    import { useI18n } from 'vue-i18n'
    import zhCn from 'element-plus/es/locale/lang/zh-cn'
    import en from 'element-plus/es/locale/lang/en'
    import EditUserInfo from './components/EditUserInfo.vue'
    import VersionLog from './components/VersionLog.vue'
    import { changeLangAPI } from './api/modules/common'
    import { isManagerAPI, signOutAPI } from './api/modules/user'
    import { ElMessageBox } from 'element-plus'

    // 国际化
    const { t } = useI18n()
    const userLocale = ref(localStorage.getItem('locale'))
    const curLocaleName = computed(() => userLocale.value === 'en' ? 'English' : '简体中文')
    const locale = computed(() => userLocale.value === 'en' ? en : zhCn)
    const toggleLang = () => {
        if (userLocale.value === 'en') {
            userLocale.value = 'zh'
            localStorage.setItem('locale', 'zh')
            changeBackendLang('zh-Hans')
        } else {
            userLocale.value = 'en'
            localStorage.setItem('locale', 'en')
            changeBackendLang('en')
        }
    }
    const changeBackendLang  = (langCode) => {
        store.commit('setMainLoading', true)
        changeLangAPI(langCode).finally(() => {
            setTimeout(() => {
                window.location.reload()
            }, 2000)
        })
    }

    const showVersionTab = () => {
        store.commit('setVersion', true)
    }

    // 宽度控制
    const width = ref(window.innerWidth)
    const height = ref(window.innerHeight)
    const isMobile = computed(() => width.value < 1000 || height.value < 600)
    const screenCheck = computed(() => route.meta.allowMobile || (width.value >= 1000 && height.value >= 600))
    onMounted(() => {
        window.addEventListener('resize', () => {
            width.value = window.innerWidth
            height.value = window.innerHeight
        })
    })

    // vuex
    const store = useStore()
    const user = computed(() => store.state.user)
    const mainLoading = computed(() => store.state.mainLoading)
    const showLogin = computed(() => store.state.showLogin)
    const showEditUser = computed(() => store.state.showEditUser)
    const showVersion = computed(() => store.state.showVersion)

    // 菜单
    const menu = ref([
        {
            name: t('Home'),
            route: {
                name: 'Home'
            },
            index: 'home',
            disabled: false
        },
        {
            name: t('Repo'),
            route: {
                name: 'Repo'
            },
            index: 'repo',
            disabled: false
        },
        {
            name: t('User'),
            route: {
                name: 'Self'
            },
            index: 'user',
            disabled: false
        },
        {
            name: t('New'),
            route: {
                name: 'Publish'
            },
            index: 'publish',
            disabled: false
        },
        {
            name: t('AdminTab'),
            route: {
                name: 'Admin'
            },
            index: 'admin',
            disabled: computed(() => !isManager.value)
        }
    ])

    // 管理员检测
    const isManager = ref(false)
    const checkManager = () => {
        isManagerAPI().then(res => {
            if (res.result && res.data) {
                isManager.value = true
            }
        })
    }
    checkManager()

    // 路由匹配
    const route = useRoute()
    const router = useRouter()
    const activeIndex = computed(() => {
        if (route.path === '/') {
            return 'home'
        }
        return route.path.split('/')[1]
    })

    // 用户信息
    onMounted(() => {
        store.dispatch('getUserInfo')
    })

    // 登录登出
    const showLogout = () => {
        const msg = t('logoutConfirm')
        ElMessageBox.alert(msg, t('logout'), {
            confirmButtonText: t('logoutConfirmed'),
            callback: action => {
                if (action === 'confirm') {
                    doLogout()
                }
            }
        })
    }
    const doLogout = () => {
        store.commit('setMainLoading', true)
        signOutAPI().then(() => {
            window.location.reload()
        }).finally(() => {
            store.dispatch('setMainLoading', false)
        })
    }

    // 加载页尾信息
    onMounted(() => {
        store.dispatch('getFooterInfo')
    })
</script>

<style>
    @import "./assets/App.css";
</style>
