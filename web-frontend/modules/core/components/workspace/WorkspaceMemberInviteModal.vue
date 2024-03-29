<template>
  <Modal>
    <h2 class="box__title">
      {{ $t('membersSettings.membersInviteModal.title') }}
    </h2>
    <Error :error="error"></Error>
    <WorkspaceInviteForm
      ref="inviteForm"
      :workspace="workspace"
      @submitted="inviteSubmitted"
    >
      <template #default>
        <div class="col col-12 align-right">
          <button
            :class="{ 'button--loading': inviteLoading }"
            class="button"
            :disabled="inviteLoading"
          >
            {{ $t('membersSettings.membersInviteModal.submit') }}
          </button>
        </div>
      </template>
      <template #roleSelectorLabel>
        <HelpIcon
          class="margin-right-1"
          :tooltip="$t('membersSettings.membersInviteModal.helpIconText')"
        />
      </template>
    </WorkspaceInviteForm>
  </Modal>
</template>

<script>
import modal from '@baserow/modules/core/mixins/modal'
import error from '@baserow/modules/core/mixins/error'
import WorkspaceInviteForm from '@baserow/modules/core/components/workspace/WorkspaceInviteForm'
import WorkspaceService from '@baserow/modules/core/services/workspace'
import { ResponseErrorMessage } from '@baserow/modules/core/plugins/clientHandler'

export default {
  name: 'MembersInviteModal',
  components: { WorkspaceInviteForm },
  mixins: [modal, error],
  props: {
    workspace: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      inviteLoading: false,
    }
  },
  methods: {
    async inviteSubmitted(values) {
      this.inviteLoading = true

      try {
        // The public accept url is the page where the user can publicly navigate too,
        // to accept the workspace invitation.
        const acceptUrl = `${this.$env.PUBLIC_WEB_FRONTEND_URL}/workspace-invitation`
        const { data } = await WorkspaceService(this.$client).sendInvitation(
          this.workspace.id,
          acceptUrl,
          values
        )
        this.$bus.$emit('invite-submitted', data)
        this.$emit('invite-submitted')
        this.hide()
      } catch (error) {
        this.handleError(error, 'workspace', {
          ERROR_GROUP_USER_ALREADY_EXISTS: new ResponseErrorMessage(
            this.$t(
              'membersSettings.membersInviteModal.errors.userAlreadyInWorkspace.title'
            ),
            this.$t(
              'membersSettings.membersInviteModal.errors.userAlreadyInWorkspace.text'
            )
          ),
        })
      }

      this.inviteLoading = false
    },
  },
}
</script>
