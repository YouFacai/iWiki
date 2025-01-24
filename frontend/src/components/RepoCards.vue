<template>
    <div>
        <el-row :gutter="20">
            <el-col :span="6" v-for="repo in repos" :key="repo.id">
                <el-card>
                    <div class="card-container">
                        <div class="text-info">
                            <div style="height: 100%; display: flex; align-items: center;">
                                <h4 style="margin-top: 0; color: var(--el-text-color-primary)">
                                    {{ repo.name }}
                                </h4>
                            </div>
                            <div style="color: var(--el-text-color-regular)">
                                <div style="display: flex; align-items: center; font-size: 14px; margin-bottom: 6px;">
                                    <el-tag size="mini" type="success" v-if="repo.r_type === 'public'" style="margin-right: 10px;">
                                        {{ $t('publicRepo') }}
                                    </el-tag>
                                    <el-tag size="mini" type="warning" v-else style="margin-right: 10px;">
                                        {{ $t('privateRepo') }}
                                    </el-tag>
                                    <i class="fa-solid fa-user" />&nbsp;{{ repo.creator_name }}
                                </div>
                                <div style="font-size: 14px;">
                                    <el-tag size="mini" type="info" style="margin-right: 10px">
                                        {{ $t('createAt') }}
                                    </el-tag>
                                    <i class="fa-solid fa-calendar-alt" />&nbsp;{{ repo.create_at }}
                                </div>
                            </div>
                        </div>
                        <div class="check-info" :class="checkUserStatus(repo) ? 'public-repo' : 'private-repo'" @click="goRepo(repo)">
                            <i class="fa-solid" :class="checkUserStatus(repo) ? 'fa-arrow-right-to-bracket' : 'fa-lock'" />
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup>
    import { useStore } from 'vuex'
    import { computed } from 'vue'
    import { useRouter } from 'vue-router'
    import message from '../utils/message'
    import { ElMessageBox } from 'element-plus'
    import { useI18n } from 'vue-i18n'
    import globalContext from '../context'
    import { applyForRepoAPI } from '../api/modules/repo'
    
    const { t } = useI18n()
    
    const store = useStore
    const user = computed(() => store.state.user)

    defineProps({
        repos: {
            type: Object,
            default: []
        }
    })

    const checkUserStatus = (repo) => {
        return repo.r_type === 'public' || repo.member_type === 'owner' || repo.member_type === 'admin' || repo.member_type === 'member'
    }
    
    const router = useRouter()
    const goRepo = (repo) => {
        if (checkUserStatus(repo)) {
            window.open(globalContext.siteUrl + 'repo/' + repo.id)
        } else {
            showApplyConfirm(repo)
        }
    }

    const showApplyConfirm = (repo) => {
        const content = t('applyMsg', { name: repo.name })
        ElMessageBox.alert(content, t('applyConfirm'), {
            confirmButtonText: t('applyConfirmed'),
            callback: (action) => {
                if (action === 'confirm') {
                    applyForRepoAPI(repo.id).then(() => {
                        message(t('applySuccess'))
                    }, err => {
                        message(err.data.msg, 'error')
                    })
                }
            },
        })
    }
</script>

<style scoped>
    .el-card {
        border: unset;
        height: 100%;
    }

    .el-card :deep(.el-card__body) {
        height: 100%;
        box-sizing: border-box;
        padding: 0;
    }

    .text-info {
        padding: 20px;
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
        justify-content: space-between;
        height: 100%;
        width: 80%;
    }

    .el-col {
        margin-bottom: 20px;
    }

    .item {
        margin-top: 0;
        margin-right: 0;
        width: 100%;
    }

    .card-container {
        display: flex;
        height: 100%;
    }

    .check-info {
        width: 21%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }

    .public-repo {
        background: var(--u-bg-color-repo-public);
        transition-duration: 0.4s;
    }

    .public-repo:hover {
        background: var(--el-color-success-light);
    }

    .private-repo {
        background: var(--u-bg-color-repo-private);
        transition-duration: 0.4s;
    }

    .private-repo:hover {
        background: var(--el-color-warning-light);
    }

    .check-info i {
        font-size: 24px;
        color: var(--el-color-white);
    }
</style>