/* mysql -h dicosql.idodeclare.org -u dicoadmin -D idodeclare_dico -p */
create fulltext index dico_petition_idx_ft on dico_petition(description);
