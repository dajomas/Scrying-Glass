for f in ci-results-* local-tests-* e2e-results/*; do git rm -rf $f; done
git commit -am "Cleanup test restult [skip ci]" && git push
for f in ci-results-* local-tests-* e2e-results/*; do rm -rf $f; done
