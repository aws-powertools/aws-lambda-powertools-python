module.exports = async ({github, context, core}) => {
    const fs = require('fs');

    const workflowRunId = core.getInput('record_pr_workflow_id');
    const artifacts = await github.rest.actions.listWorkflowRunArtifacts({
      owner: context.repo.owner,
      repo: context.repo.repo,
      run_id: workflowRunId,
    });

    const matchArtifact = artifacts.data.artifacts.filter(artifact => artifact.name == "pr")[0];

    const artifact = await github.rest.actions.downloadArtifact({
      owner: context.repo.owner,
      repo: context.repo.repo,
      artifact_id: matchArtifact.id,
      archive_format: 'zip',
    });

    fs.writeFileSync('${{github.workspace}}/pr.zip', Buffer.from(artifact.data));
}
