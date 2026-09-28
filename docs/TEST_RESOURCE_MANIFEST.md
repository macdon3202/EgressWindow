# Test resource manifest

## Production retrieval policy

The contract constructs exactly one GitHub API route from a closed authority
catalog and a normalized release tag:

```text
https://api.github.com/repos/{fixed-owner}/{fixed-repository}/releases/tags/{tag}
```

The returned `html_url` and `tag_name` must exactly match the bound authority
and tag. The content digest is recomputed from the fetched release ID, tag,
canonical URL, publication timestamp and body.

## Local fixtures

Local tests use explicitly synthetic GitHub API JSON and model responses. They
are behavioral fixtures only and must never be presented as live source proof.
They cover source errors, binding mismatch, malformed model output, unknown
facts, short windows, exceptions, role separation, replay and rollback.

## Live evidence rule

A submission may call a path live only when it records:

- exact deployed address and source hash;
- actual allowed authority and existing release tag;
- expected result written before execution;
- every transaction hash;
- finalized consensus and leader execution result;
- exact pre/post readbacks;
- claim limitations of that particular notice.

An official release without an exit disclosure is a valid negative fixture. It
must not be described as evidence that the protocol breached a policy.
