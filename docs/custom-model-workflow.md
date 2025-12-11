# Updating an Apheris Model Registry Model

To update the model in Apheris, you must first commit your code in a Git repository:

```console
git commit -m "my code changes"
```

Keep a note of the commit hash, as you'll need this later.

Now build the Dockerfile locally. You should tag the model for the Apheris Quay repository
where your model will be stored. The version number must be compatible with
[Semantic Versioning 2.0.0](https://semver.org/#semantic-versioning-200), so `0.1.2` and
`1.2.3-alpha.0.1.234` are valid, but `new-model-0.1.2` is not.

```console
docker build -t quay.io/apheris/<repo_name>:<version_number>  .
```

> [!IMPORTANT]
> If you're building on a Mac, you might need to cross-compile for an x86
architecture in order to support the Orchestrator and Gateway hardware architectures.
> To do this, add the `--platform="linux/amd64"` flag to the `docker build` command.

You can alternatively tag an existing image to add to Quay:

```console
docker tag <existing-image-tag> quay.io/apheris/<repo_name>:<version_number>
```

Then you push the model to the Quay repo:

```console
docker push quay.io/apheris/<repo_name>:<version_number>
```

When you push an image to Quay, you'll receive a digest, starting with `sha256:...`. Keep
a note of this as you'll need it in the next step, in addition to the commit hash from
earlier.

Finally, use the Apheris CLI to update the model version in the model registry:

```console
apheris models add-version --version <version_number> --engine nvflare:2.5.2 --digest <digest> --commit-hash <hash> <model_id>
```

* `<version_number>` must match the tag pushed to Quay.
* `<digest>` is the digest from your `docker push` command, including the `sha256` prefix.
* `<hash>` is the commit hash referring to your code changes.
* `<model_id>` is the ID of the model in the Apheris model registry.
