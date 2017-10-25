# CYK-Parser-for-Probabilistic-Context-Free-Grammars-Python

function CKY-PARSE(words, grammar) returns table
    for j←from 1 to LENGTH(words) do
      for all {A | A → words[ j] ∈ grammar}
          table[j −1, j]←table[j −1, j] ∪ A
          for i←from j −2 downto 0 do
            for k←i+1 to j −1 do
               for all {A | A → BC ∈ grammar and B ∈ table[i, k] andC ∈ table[k, j]}
                table[i,j]←table[i,j] ∪ A
